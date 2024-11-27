from Acquisition import aq_inner
from collections import defaultdict
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement, IPloneRestapiLayer
from plone.restapi.services.navigation.get import Navigation as BaseNavigation
from plone.restapi.services.navigation.get import \
    NavigationGet as BaseNavigationGet
from plone.restapi.serializer.converters import json_compatible
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.browser.navigation import \
    CatalogNavigationTabs as BaseCatalogNavigationTabs
from Products.CMFPlone.browser.navigation import get_id, get_view_url
from urllib.parse import urlparse
from zope.component import adapter, getMultiAdapter, getUtility
from zope.interface import Interface, implementer
from zope.i18n import translate


# if '/mission' not in self.context.absolute_url(relative=True):
def is_outside_mission(context):
    bits = context.getPhysicalPath()
    if len(bits) > 3 and bits[3] == "mission":
        return False

    return True


class CustomCatalogNavigationTabs(BaseCatalogNavigationTabs):
    def customize_entry(self, entry, brain=None):
        if brain and hasattr(brain, "nav_title") and brain.nav_title:
            entry["title"] = brain.nav_title

    # customized to add support for nav_title
    def topLevelTabs(self, actions=None, category="portal_tabs"):
        context = aq_inner(self.context)

        mtool = getToolByName(context, "portal_membership")
        member = mtool.getAuthenticatedMember().id

        portal_properties = getToolByName(context, "portal_properties")
        self.navtree_properties = getattr(portal_properties, "navtree_properties")
        self.site_properties = getattr(portal_properties, "site_properties")
        self.portal_catalog = getToolByName(context, "portal_catalog")

        if actions is None:
            context_state = getMultiAdapter(
                (context, self.request), name="plone_context_state"
            )
            actions = context_state.actions(category)

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions:
                data = actionInfo.copy()
                data["name"] = data["title"]
                result.append(data)

        # check whether we only want actions
        if self.site_properties.getProperty("disable_folder_sections", False):
            return result

        query = self._getNavQuery()

        rawresult = self.portal_catalog.searchResults(query)

        def get_link_url(item):
            linkremote = item.getRemoteUrl and not member == item.Creator
            if linkremote:
                return (get_id(item), item.getRemoteUrl)
            else:
                return False

        # now add the content to results
        idsNotToList = self.navtree_properties.getProperty("idsNotToList", ())
        # __import__("pdb").set_trace()
        for item in rawresult:
            if not (item.getId in idsNotToList or item.exclude_from_nav):
                id, item_url = get_link_url(item) or get_view_url(item)
                data = {
                    "name": utils.pretty_title_or_id(context, item),
                    "id": item.getId,
                    "url": item_url,
                    "description": item.Description,
                }
                self.customize_entry(data, item)
                result.append(data)

        return result

    def _getNavQuery(self):
        query = super(CustomCatalogNavigationTabs, self)._getNavQuery()

        if not is_outside_mission(self.context):
            return query

        query["show_in_top_level"] = True

        return query


def fix_url(url):
    return url.replace("/cca/", "/")


@implementer(IExpandableElement)
@adapter(Interface, IPloneRestapiLayer)
class Navigation(BaseNavigation):
    def __call__(self, expand=False):
        if self.request.form.get("expand.navigation.depth", False):
            # self.depth = int(self.request.form["expand.navigation.depth"])

            if is_outside_mission(self.context):
                self.depth = 8
            else:
                self.depth = int(self.request.form["expand.navigation.depth"])
        else:
            self.depth = 1

        result = {"navigation": {"@id": self.context.absolute_url() + "/@navigation"}}
        if not expand:
            return result

        result["navigation"]["items"] = self.build_tree(self.navtree_path)
        return result

    @property
    @memoize
    def navtree(self):
        ret = defaultdict(list)
        navtree_path = self.navtree_path
        for tab in self.portal_tabs:
            entry = {}
            entry.update(
                {
                    "path": "/".join((navtree_path, tab["id"])),
                    "description": tab["description"],
                    "@id": tab["url"],
                }
            )
            if "review_state" in tab:
                entry["review_state"] = json_compatible(tab["review_state"])
            else:
                entry["review_state"] = None

            if "title" not in entry:
                entry["title"] = tab.get("name") or tab.get("description") or tab["id"]
            else:
                # translate Home tab
                entry["title"] = translate(
                    entry["title"], domain="plone", context=self.request
                )

            entry["title"] = safe_unicode(entry["title"])
            ret[navtree_path].append(entry)

        query = {
            "path": {
                "query": self.navtree_path,
                "depth": self.depth,
            },
            "portal_type": {"query": self.settings["displayed_types"]},
            "Language": self.current_language,
            "is_default_page": False,
            "sort_on": "getObjPositionInParent",
        }

        if not self.settings["nonfolderish_tabs"]:
            query["is_folderish"] = True

        if self.settings["filter_on_workflow"]:
            query["review_state"] = list(self.settings["workflow_states_to_show"] or ())

        if not self.settings["show_excluded_items"]:
            query["exclude_from_nav"] = False

        context_path = "/".join(self.context.getPhysicalPath())
        portal_catalog = getToolByName(self.context, "portal_catalog")
        brains = portal_catalog.searchResults(**query)

        registry = getUtility(IRegistry)
        types_using_view = registry.get("plone.types_use_view_action_in_listings", [])

        for brain in brains:
            brain_path = brain.getPath()
            brain_parent_path = brain_path.rpartition("/")[0]
            if brain_parent_path == navtree_path:
                # This should be already provided by the portal_tabs_view
                continue
            # Customization:
            # Remove `and not context_path.startswith(brain_path)` from the condition
            # to ensure we skip items marked as excluded (exclude_from_nav) even 
            # if they are in the current context path.
            if brain.exclude_from_nav:
                continue
            url = brain.getURL()
            entry = {
                "path": brain_path,
                "@id": url,
                "title": safe_unicode(brain.Title),
                "description": safe_unicode(brain.Description),
                "review_state": json_compatible(brain.review_state),
                "use_view_action_in_listings": brain.portal_type in types_using_view,
            }

            if brain.get("nav_title", False):
                entry.update({"title": brain["nav_title"]})

            self.customize_entry(entry, brain)
            ret[brain_parent_path].append(entry)
        return ret

    def customize_entry(self, entry, brain):
        entry["brain"] = brain

        if getattr(brain, "is_nonstructural_folder", False):
            entry["nonclickable"] = True

        if hasattr(brain, "getRemoteUrl") and brain.getRemoteUrl:
            entry["path"] = urlparse(brain.getRemoteUrl).path
            entry["@id"] = fix_url(brain.getRemoteUrl)

        if hasattr(brain, "nav_title") and brain.nav_title:
            entry["title"] = brain.nav_title

        return entry

    def render_item(self, item, path):
        if 'path' not in item:
            # TODO: weird case, to be analysed
            if "brain" in item:
                del item["brain"]
            return item
        sub = self.build_tree(item["path"], first_run=False)

        item.update({"items": sub})

        if "path" in item:
            del item["path"]

        if "brain" in item:
            del item["brain"]

        return item

    @property
    @memoize
    def portal_tabs(self):
        # __import__("pdb").set_trace()
        old = super(Navigation, self).portal_tabs
        for entry in old:
            if entry.get("url"):
                # quick hack to fix broken handling of Link Urls
                entry["url"] = fix_url(entry["url"])
            if entry.get("title"):
                entry["name"] = entry["title"]
        return old


class NavigationGet(BaseNavigationGet):
    def reply(self):
        navigation = Navigation(self.context, self.request)
        return navigation(expand=True)["navigation"]
