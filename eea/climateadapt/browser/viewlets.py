import pkg_resources
from Acquisition import aq_inner
from plone.api import group
from plone.api.content import get_state
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import PathBarViewlet as BasePathBarViewlet
from plone.app.layout.viewlets.common import (
    PersonalBarViewlet as BasePersonalBarViewlet,
)
from plone.app.layout.viewlets.common import SearchBoxViewlet as BaseSearchViewlet
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
# from tlspu.cookiepolicy.browser.viewlets import CookiePolicyViewlet
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.site.hooks import getSite
# from eea.climateadapt.translation.utils import TranslationUtilsMixin
# from eea.climateadapt.translation.core import get_translation_object
# from eea.climateadapt.translation.utils import get_current_language
from plone.api import portal

# from Products.LDAPUserFolder.LDAPDelegate import filter_format

try:
    pkg_resources.get_distribution("plone.app.relationfield")
except pkg_resources.DistributionNotFound:
    HAS_RELATIONFIELD = False
else:
    from plone.app.relationfield.behavior import IRelatedItems

    HAS_RELATIONFIELD = True


def redirect_to_personal_preferences():
    site = getSite()
    request = getRequest()

    messages = IStatusMessage(request)
    messages.add(
        "Please complete your profile by adding your Professional "
        + "thematic domain.",
        type="info",
    )

    if request.get("came_from", None):
        request["came_from"] = ""
        request.form["came_from"] = ""

    edit_profile_url = site.portal_url() + "/@@personal-preferences"
    request.RESPONSE.redirect(edit_profile_url)


def check_sectors(user):
    our_group = group.get("extranet-cca-thematicexperts")
    if our_group is None:
        return False
    user_ids = our_group.getAllGroupMemberIds()
    sectors = user.getProperty("thematic_sectors", "")

    if sectors == "" and user.id in user_ids:
        return True
    else:
        return False


class CustomizedPersonalBarViewlet(BasePersonalBarViewlet):
    """Redirect users who belong to extranet-cca-thematicexperts group to
    personal-preferences page
    """

    def update(self):
        super(CustomizedPersonalBarViewlet, self).update()

        if not self.anonymous:
            mt = getToolByName(self, "portal_membership")
            user = mt.getAuthenticatedMember()

            if self.request.getURL() != (self.portal_url + "/@@personal-preferences"):
                if check_sectors(user):
                    redirect_to_personal_preferences()


# TODO add TranslationUtilsMixin to inheritance
class SharePageSubMenuViewlet(ViewletBase):
    index = ViewPageTemplateFile("pt/viewlet_sharepage_submenu.pt")

    def update(self):
        super(SharePageSubMenuViewlet, self).update()
        self.base_url = "/".join((self.context.portal_url(),
                                 "share-your-info"))


class PolicySectorPageSubMenuViewlet(ViewletBase):
    index = ViewPageTemplateFile("pt/viewlet_policysectorpage_submenu.pt")


class SearchBoxViewlet(BaseSearchViewlet):
    index = ViewPageTemplateFile("pt/searchbox.pt")


class RelatedItemsViewlet(ViewletBase):
    """Override to hide files and images in the related content viewlet"""

    def related_items(self):
        context = aq_inner(self.context)
        res = ()

        site_url = portal.getSite().absolute_url()
        # current_language = get_current_language(self.context, self.request)
        current_language = 'en'
        if current_language != "en":
            en_obj = None # get_translation_object(context, "en")
            if en_obj is None:
                en_obj = context  # case of not translated items (Newsletter)
        else:
            en_obj = context

        catalog = getToolByName(en_obj, "portal_catalog")

        # Archetypes

        if base_hasattr(en_obj, "getRawRelatedItems"):
            related = en_obj.getRawRelatedItems()

            if not related:
                return ()
            brains = catalog(UID=related)

            if brains:
                # build a position dict by iterating over the items once
                positions = dict([(v, i) for (i, v) in enumerate(related)])
                # We need to keep the ordering intact
                res = list(brains)

                def _key(brain):
                    return positions.get(brain.UID, -1)

                res.sort(key=_key)

        # Dexterity

        if HAS_RELATIONFIELD and IRelatedItems.providedBy(en_obj):
            related = en_obj.relatedItems

            if not related:
                return ()
            res = self.related2brains(related)

        translated_res = []
        for brain in res:
            en_obj = brain.getObject()
            try:
                trans_obj = en_obj # get_translation_object(en_obj, current_language)
                obj_url = trans_obj.absolute_url()
                obj_path = "/cca" + obj_url.split(site_url)[-1]

                trans_res = catalog({"path": obj_path})
                translated_res.append(trans_res[0])
            except Exception:
                pass
        return translated_res

    def related2brains(self, related):
        """Return a list of brains based on a list of relations. Will filter
        relations if the user has no permission to access the content.

        :param related: related items
        :type related: list of relations
        :return: list of catalog brains
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = []

        for r in related:
            path = r.to_path
            # the query will return an empty list if the user has no
            # permission to see the target object
            brains.extend(catalog(path=dict(query=path, depth=0)))

        res = []

        for b in brains:
            if b.getObject().portal_type not in ["File", "Image"]:
                res.append(b)

        return res


class PathBarViewlet(BasePathBarViewlet):
    """Override to hide the breadcrumbs on the frontpage"""

    render = ViewPageTemplateFile("pt/breadcrumbs.pt")

    def render(self):
        if not self.context.id == "frontpage":
            return super(PathBarViewlet, self).render()

        if IPloneSiteRoot.providedBy(self.context.aq_parent):
            return ""

    def update(self):
        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        self.navigation_root_url = portal_state.navigation_root_url()

        self.is_rtl = portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter(
            (self.context, self.request), name="breadcrumbs_view"
        )
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
        self.br_exists = True

        if self.context.id == "frontpage":
            self.br_exists = False

    def localize_observatory(self, url):
        # import pdb; pdb.set_trace()
        portal_url = self.context.portal_url()
        base = self.navigation_root_url

        current_lang = self.request.cookies.get("I18N_LANGUAGE", "en")
        if "/observatory/metadata" in url:
            path = url.replace(portal_url, "")
            path = path.replace("/%s/observatory/" % current_lang, "")
            url = base + "/++aq++" + path

        if "/observatory/news-archive" in url:
            url = "/%s/observatory/news-archive-observatory/" % current_lang

        if "/observatory/more-events" in url:
            url = "%s/observatory/more-events-observatory/" % current_lang

        return url


# class CookiesViewlet(CookiePolicyViewlet):
#     render = ViewPageTemplateFile("pt/cookiepolicy.pt")

#     def update(self):
#         return super(CookiesViewlet, self).render()


class ArchivedStateViewlet(ViewletBase):
    index = ViewPageTemplateFile("pt/archived_state_viewlet.pt")

    def render(self):
        try:
            state = get_state(self.context)
        except WorkflowException:
            return ""

        if state == "archived":
            return self.index()

        return ""
