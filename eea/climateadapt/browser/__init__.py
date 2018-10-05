import json
import logging
from collections import namedtuple

from collective.cover.browser.cover import Standard

from AccessControl import getSecurityManager
from Acquisition import aq_inner
from eea.climateadapt.vocabulary import (BIOREGIONS, SUBNATIONAL_REGIONS,
                                         ace_countries_dict)
from plone import api
from plone.api.user import get
from plone.app.iterate.browser.control import Control
from plone.app.iterate.interfaces import (ICheckinCheckoutPolicy,
                                          IIterateAware, IObjectArchiver,
                                          IWorkingCopy)
from plone.app.iterate.permissions import CheckinPermission, CheckoutPermission
from plone.memoize import view
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zExceptions import NotFound

logger = logging.getLogger('eea.climateadapt')

ReviewInfo = namedtuple('ReviewInfo', ['creator', 'reviewer'])


class AceViewApi(object):

    def get_review_info(self):
        """ Return review information.

        See https://taskman.eionet.europa.eu/issues/90376
        """

        creator = self.context.Creator()
        reviewer = None

        if creator is 'tibi':
            creator = None

        wh = self.context.workflow_history
        wf = wh['cca_items_workflow']

        for reviewer_metadata in wf:
            if reviewer_metadata['review_state'] == 'published':
                reviewer = reviewer_metadata['actor']

        if creator:
            member = get(creator)

            if member:
                creator = member.getProperty('fullname') or creator

        if reviewer:
            member = get(reviewer)

            if member:
                reviewer = member.getProperty('fullname') or reviewer

        return ReviewInfo(creator, reviewer)

    @view.memoize
    def html2text(self, html):
        if not isinstance(html, basestring):
            return u""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()

        return text.strip()

    def linkify(self, text):
        if not text:
            return

        if text.startswith('/') or text.startswith('http'):
            return text

        return "http://" + text

    def get_websites(self):
        """ This returns a list of websites. Because of BBB, we need to treat
        them in various ways
        """
        websites = self.context.websites

        result = []

        for link in websites:
            result.append({'url': self.linkify(link), 'title': link})

        return result

    def get_files(self):
        files = self.context.contentValues({'portal_type': 'File'})

        for r in self.context.relatedItems:
            if r.to_object.portal_type in ['File', 'Image']:
                files.append(r.to_object)

        # return [r.to_object for r in self.context.relatedItems] \
        #     + self.context.contentValues({'portal_type': 'File'})

        return files

    def _render_geochar_element(self, value):
        value = BIOREGIONS[value]

        return u"<p>{0}</p>".format(value)
        # if value == 'Global':
        #     return value + u"<br/>"
        # else:
        #     return value + u":<br/>"

    def _render_geochar_macrotrans(self, value):
        tpl = (u"<div class='sidebar_bold'>"
               u"<h5>Macro-Transnational region:</h5><p>{0}</p></div>")

        return tpl.format(u", ".join([BIOREGIONS[x] for x in value]))

    def _render_geochar_biotrans(self, value):
        tpl = (u"<div class='sidebar_bold'>"
               u"<h5>Biographical regions:</h5><p>{0}</p></div>")

        return tpl.format(u", ".join([BIOREGIONS.get(x, x) for x in value]))

    def _render_geochar_countries(self, value):
        tpl = u"<div class='sidebar_bold'><h5>Countries:</h5><p>{0}</p></div>"

        return tpl.format(u", ".join(self.get_countries(value)))

    def _render_geochar_subnational(self, value):
        tpl = (u"<div class='sidebar_bold'>"
               u"<h5>Sub Nationals:</h5><p>{0}</p></div>")
        # a list like: ['SUBN_Marche__IT_']

        out = []

        for line in value:
            line = line.encode('utf-8')

            if line in SUBNATIONAL_REGIONS:
                out.append(SUBNATIONAL_REGIONS[line])

                continue
            else:
                logger.error("Subnational region not found: %s", line)

        text = u", ".join([x.decode('utf-8') for x in out])

        return tpl.format(text)

    def _render_geochar_city(self, value):
        text = value

        if isinstance(value, (list, tuple)):
            text = u", ".join(value)

        return (u"<div class='sidebar_bold'>"
                u"<h5>City:</h5><p>{0}</p></div>".format(text))

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
            return u""

        value = json.loads(value)

        out = []
        order = ['element', 'macrotrans', 'biotrans',
                 'countries', 'subnational', 'city']

        for key in order:
            element = value['geoElements'].get(key)

            if element:
                renderer = getattr(self, "_render_geochar_" + key)
                out.append(renderer(element))

        return u" ".join(out)

    def link_to_original(self):
        """ Returns link to original object, to allow easy comparison
        """
        site = "http://climate-adapt-old.eea.europa.eu"

        if hasattr(self.context, '_aceitem_id'):
            return ("{0}/viewaceitem?aceitem_id={1}".format(
                site, self.context._aceitem_id))

        if hasattr(self.context, '_acemeasure_id'):
            return ("{0}/viewmeasure?ace_measure_id={1}".format(
                site, self.context._acemeasure_id))

        if hasattr(self.context, '_aceproject_id'):
            return (
                "{0}/projects1?ace_project_id={1}".format(
                    site, self.context._aceproject_id))

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
        mt = getToolByName(self.context, 'portal_membership')
        groups_tool = getToolByName(self.context, 'portal_groups')
        user = mt.getAuthenticatedMember()

        user_groups = [group.id
                       for group in groups_tool.getGroupsByUserId(user.id)]
        to_check = ['extranet-cca-reviewers',
                    'Administrators',
                    'extranet-cca-powerusers',
                    'extranet-cca-managers']
        check_roles = [group for group in user_groups if group in to_check]

        if len(check_roles) > 0:
            return True

        return False


class ViewAceItem(BrowserView):
    """ Redirection view for /viewaceitem?aceitem_id=..."
    """

    def __call__(self, REQUEST):

        aceitem_id = REQUEST.get('aceitem_id')

        if aceitem_id:
            try:
                aceitem_id = int(aceitem_id)
            except ValueError:
                raise NotFound
        else:
            raise NotFound

        return redirect(self.context, REQUEST, 'aceitem_id', aceitem_id)


class ViewAceMeasure(BrowserView):
    """ Redirection view for /viewacemeasure?ace_measure_id=..."
    """

    def __call__(self, REQUEST):

        acemeasure_id = REQUEST.get('ace_measure_id')

        if (not acemeasure_id) or (not acemeasure_id.isdigit()):
            raise NotFound

        acemeasure_id = int(acemeasure_id)

        return redirect(self.context, REQUEST, 'acemeasure_id', acemeasure_id)


class ViewAceProject(BrowserView):
    """ Redirection view for /project1?ace_project_id=..."
    """

    def __call__(self, REQUEST):

        aceproject_id = REQUEST.get('ace_project_id')

        if not aceproject_id or not aceproject_id.isdigit():
            raise NotFound

        aceproject_id = int(aceproject_id)

        return redirect(self.context, REQUEST, 'aceproject_id', aceproject_id)


def redirect(site, REQUEST, key, itemid):
    portal_catalog = site.portal_catalog
    brains = portal_catalog({key: itemid})

    if not brains:
        raise NotFound
    ob = brains[0].getObject()

    return REQUEST.RESPONSE.redirect(ob.absolute_url(), status=301)


class CoverNoTitleView(Standard):
    """ A template for covers that doesn't include the title
    """

    def __call__(self):
        return self.index()


class IterateControl(Control):
    """ Better behaviour for plone.app.iterate
    """

    def is_checkout(self):
        """ Is this object a checkout? Used by CCA for workflow guards
        """
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
        """ Overrided to check for the checkin permission, as it should be normal
        """

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
        except:
            return False

        if original is None:
            return False

        checkPermission = getSecurityManager().checkPermission

        if not checkPermission(CheckinPermission, original):
            return False

        return True

    def checkout_allowed(self):
        """ Overrided to check for the checkout permission, as it is normal
        """
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

        has_wc = (wc is not None)
        is_wc = (self.context.aq_inner.aq_self is wc.aq_inner.aq_self)
        res = has_wc and is_wc
        print "Checkout cancel allowed: ", res

        return res
