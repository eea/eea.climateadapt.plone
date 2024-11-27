import json
import logging
from collections import namedtuple

from AccessControl import getSecurityManager
from Acquisition import aq_inner
# from collective.cover.browser.cover import Standard
from eea.climateadapt.vocabulary import (
    BIOREGIONS,
    SUBNATIONAL_REGIONS,
    ace_countries_dict,
)
from eea.climateadapt import MessageFactory as _
# from eea.climateadapt.translation.utils import translate_text
from eea.geotags.behavior.geotags import ISingleGeoTag
from plone import api
from plone.api.user import get
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import (
    ICheckinCheckoutPolicy,
    IIterateAware,
    IObjectArchiver,
    IWorkingCopy,
)
from plone.app.iterate.permissions import CheckinPermission, CheckoutPermission
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zExceptions import NotFound
from zope.component import queryAdapter


logger = logging.getLogger("eea.climateadapt")

ReviewInfo = namedtuple("ReviewInfo", ["creator", "reviewer"])


def get_date_updated(item):
    wh = item.workflow_history
    wf = wh.get("cca_items_workflow", None)

    response = {}
    response["cadapt_last_modified"] = item.modified()
    response["cadapt_published"] = item.effective()

    if not wf:
        return response

    for metadata in wf:
        if metadata["action"] == "publish":
            response["cadapt_published"] = metadata["time"]

    return response


def get_files(context):
    files = context.contentValues({"portal_type": "File"})

    if context.relatedItems is None:
        return files

    for r in context.relatedItems:
        obj = r.to_object
        if obj is None:
            continue
        if obj.portal_type in ["File", "Image"]:
            files.append(obj)

    # return [r.to_object for r in self.context.relatedItems] \
    #     + self.context.contentValues({'portal_type': 'File'})

    return files


class AceViewApi(object):
    def geotag(self):
        tag = queryAdapter(self.context, ISingleGeoTag)

        return tag

    def get_review_info(self):
        """Return review information.
        See https://taskman.eionet.europa.eu/issues/90376
        """

        creator = self.context.Creator()
        reviewer = None

        if creator == "tibi":
            creator = None

        wh = self.context.workflow_history
        wf = wh.get("cca_items_workflow", None)

        if not wf:
            return None

        for reviewer_metadata in wf:
            if reviewer_metadata["review_state"] == "published":
                reviewer = reviewer_metadata["actor"]

        if creator:
            member = get(creator)

            if member:
                creator = member.getProperty("fullname") or creator

        if reviewer:
            member = get(reviewer)

            if member:
                reviewer = member.getProperty("fullname") or reviewer

        return ReviewInfo(creator, reviewer)

    def get_date_updated(self):
        return get_date_updated(self.context)

    def hide_back_to_search_button(self):
        if self.request.form.get("bs") != "1":
            return 0
        return 1

    @view.memoize
    def html2text(self, html):
        if not isinstance(html, str):
            return ""
        portal_transforms = api.portal.get_tool(name="portal_transforms")
        data = portal_transforms.convertTo(
            "text/plain", html, mimetype="text/html")
        text = data.getData()

        return text.strip()

    def linkify(self, text):
        if not text:
            return

        if text.startswith("/") or text.startswith("http"):
            return text

        return "http://" + text

    def get_websites(self, field_name="websites"):
        """This returns a list of websites. Because of BBB, we need to treat
        them in various ways
        """

        result = []

        if not hasattr(self.context, field_name):
            return result

        websites = getattr(self.context, field_name)
        if websites is None:
            return result

        for link in websites:
            result.append({"url": self.linkify(link), "title": link})

        return result

    def get_files(self):
        return get_files(self.context)

    def _render_geochar_element(self, value):
        value = BIOREGIONS[value]

        return "<p>{0}</p>".format(value)
        # if value == 'Global':
        #     return value + u"<br/>"
        # else:
        #     return value + u":<br/>"

    def _render_geochar_macrotrans(self, value):
        tpl = (
            "<div class='sidebar_bold'>"
            "<h5>" +
            self.translate_text(
                _("Macro-Transnational region"))+":</h5><p>{0}</p></div>"
        )

        return tpl.format(", ".join([BIOREGIONS[x] for x in value]))

    def _render_geochar_biotrans(self, value):
        tpl = (
            "<div class='sidebar_bold'>"
            "<h5>" +
            self.translate_text(_("Biogeographical regions")
                                )+":</h5><p>{0}</p></div>"
        )

        return tpl.format(", ".join([BIOREGIONS.get(x, x) for x in value]))

    def _render_geochar_countries(self, value):
        tpl = "<div class='sidebar_bold'><h5>" + \
            self.translate_text(_("Countries"))+":</h5><p>{0}</p></div>"

        return tpl.format(", ".join(self.get_countries(value)))

    def _render_geochar_subnational(self, value):
        label = self.translate_text(_('Sub Nationals'))
        tpl = "<div class='sidebar_bold'>" "<h5>%s:</h5><p>{0}</p></div>" % label
        # tpl = u"<div class='sidebar_bold'>" u"<h5>"+_(u"Sub Nationals")+":</h5><p>{0}</p></div>"

        # a list like: ['SUBN_Marche__IT_']

        out = []

        for line in value:
            line = line.encode("utf-8")

            if line in SUBNATIONAL_REGIONS:
                out.append(SUBNATIONAL_REGIONS[line])

                continue
            else:
                logger.error("Subnational region not found: %s", line)

        text = ", ".join([x.decode("utf-8") for x in out])

        return tpl.format(text)

    def _render_geochar_city(self, value):
        text = value

        if isinstance(value, (list, tuple)):
            text = ", ".join(value)

        return "<div class='sidebar_bold'>" "<h5>{0}:</h5><p>{1}</p></div>".format(
            self.translate_text(_("City")),
            text
        )

    @view.memoize
    def render_geochar(self, value):
        # value is a mapping such as:
        # u'{"geoElements":{"element":"EUROPE",
        #                   "macrotrans":["TRANS_MACRO_ALP_SPACE"],
        #                   "biotrans":[],
        #                   "countries":[],
        #                   "subnational":[],
        #                   "city":""}}'

        if not value:
            return ""

        value = json.loads(value)

        out = []
        order = [
            "element",
            "macrotrans",
            "biotrans",
            "countries",
            "subnational",
            "city",
        ]

        """ At observatory partner page for organisations remove
        a few categorizations
        """

        if (
            "observatory_page" in self.request.form
            and self.context.include_in_observatory
            and self.context.search_type == "ORGANISATION"
        ):
            if "macrotrans" in order:
                order.remove("biotrans")
            if "countries" in order:
                order.remove("countries")
            if "subnational" in order:
                order.remove("subnational")
            if "city" in order:
                order.remove("city")

        for key in order:
            element = value["geoElements"].get(key)

            if element:
                renderer = getattr(self, "_render_geochar_" + key)
                out.append(renderer(element))

        return " ".join(out)

    def link_to_original(self):
        """Returns link to original object, to allow easy comparison"""
        site = "http://climate-adapt-old.eea.europa.eu"

        if hasattr(self.context, "_aceitem_id"):
            return "{0}/viewaceitem?aceitem_id={1}".format(
                site, self.context._aceitem_id
            )

        if hasattr(self.context, "_acemeasure_id"):
            return "{0}/viewmeasure?ace_measure_id={1}".format(
                site, self.context._acemeasure_id
            )

        if hasattr(self.context, "_aceproject_id"):
            return "{0}/projects1?ace_project_id={1}".format(
                site, self.context._aceproject_id
            )

    def get_countries(self, country_list):
        return [ace_countries_dict.get(x, x) for x in country_list]

    def type_label(self):
        from eea.climateadapt.vocabulary import _datatypes

        d = dict(_datatypes)

        return d[self.context.search_type]

    def governance_level(self):
        if self.context.governance_level is None:
            return ""

        if len(self.context.governance_level) == 0:
            return ""

        from eea.climateadapt.vocabulary import _governance

        d = dict(_governance)

        return [d.get(b) for b in self.context.governance_level]

    def check_user_role(self):
        mt = getToolByName(self.context, "portal_membership")
        groups_tool = getToolByName(self.context, "portal_groups")
        user = mt.getAuthenticatedMember()

        user_groups = [
            group.id for group in groups_tool.getGroupsByUserId(user.id)]
        to_check = [
            "extranet-cca-reviewers",
            "Administrators",
            "extranet-cca-powerusers",
            "extranet-cca-managers",
        ]
        check_roles = [group for group in user_groups if group in to_check]

        if len(check_roles) > 0:
            return True

        return False

    def translate_text(self, text):
        # TODO translate text
        # return translate_text(self.context, self.request, text)

        return text


class ViewAceItem(BrowserView):
    """Redirection view for /viewaceitem?aceitem_id=..." """

    def __call__(self, REQUEST):
        aceitem_id = REQUEST.get("aceitem_id")

        if aceitem_id:
            try:
                aceitem_id = int(aceitem_id)
            except ValueError:
                raise NotFound
        else:
            raise NotFound

        return redirect(self.context, REQUEST, "aceitem_id", aceitem_id)


class ViewAceMeasure(BrowserView):
    """Redirection view for /viewacemeasure?ace_measure_id=..." """

    def __call__(self, REQUEST):
        acemeasure_id = REQUEST.get("ace_measure_id")

        if (not acemeasure_id) or (not acemeasure_id.isdigit()):
            raise NotFound

        acemeasure_id = int(acemeasure_id)

        return redirect(self.context, REQUEST, "acemeasure_id", acemeasure_id)


class ViewAceProject(BrowserView):
    """Redirection view for /project1?ace_project_id=..." """

    def __call__(self, REQUEST):
        aceproject_id = REQUEST.get("ace_project_id")

        if not aceproject_id or not aceproject_id.isdigit():
            raise NotFound

        aceproject_id = int(aceproject_id)

        return redirect(self.context, REQUEST, "aceproject_id", aceproject_id)


def redirect(site, REQUEST, key, itemid):
    portal_catalog = site.portal_catalog
    brains = portal_catalog({key: itemid})

    if not brains:
        raise NotFound
    ob = brains[0].getObject()

    return REQUEST.RESPONSE.redirect(ob.absolute_url(), status=301)


# class CoverNoTitleView(Standard):
#     """A template for covers that doesn't include the title"""

#     def __call__(self):
#         return self.index()


class IterateControl(Control):
    """Better behaviour for plone.app.iterate"""

    def is_checkout(self):
        """Is this object a checkout? Used by CCA for workflow guards"""
        context = aq_inner(self.context)

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)

        if not archiver.isVersionable():
            return False

        if IWorkingCopy.providedBy(context):
            return True

        return False

    def checkin_allowed(self):
        """Overrided to check for the checkin permission, as it should be normal"""

        context = aq_inner(self.context)
        checkPermission = getSecurityManager().checkPermission

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)

        if not archiver.isVersionable():
            return False

        if not IWorkingCopy.providedBy(context):
            return False

        policy = ICheckinCheckoutPolicy(context, None)

        if policy is None:
            return False

        try:
            original = policy.getBaseline()
        except Exception:
            return False

        if original is None:
            return False

        checkPermission = getSecurityManager().checkPermission

        if not checkPermission(CheckinPermission, original):
            return False

        return True

    def checkout_allowed(self):
        """Overrided to check for the checkout permission, as it is normal"""
        context = aq_inner(self.context)

        if not IIterateAware.providedBy(context):
            return False

        archiver = IObjectArchiver(context)

        if not archiver.isVersionable():
            return False

        policy = ICheckinCheckoutPolicy(context, None)

        if policy is None:
            return False

        if policy.getWorkingCopy() is not None:
            return False

        # check if its is a checkout

        if policy.getBaseline() is not None:
            return False

        checkPermission = getSecurityManager().checkPermission

        if not checkPermission(CheckoutPermission, context):
            return False

        return True

    def cancel_allowed(self):
        """Check to see if the user can cancel the checkout on the given
        working copy.
        """
        policy = ICheckinCheckoutPolicy(self.context, None)

        if policy is None:
            return False
        wc = policy.getWorkingCopy()

        if wc is None:
            return False

        has_wc = wc is not None
        is_wc = self.context.aq_inner.aq_self is wc.aq_inner.aq_self
        res = has_wc and is_wc
        print(("Checkout cancel allowed: ", res))

        return res
