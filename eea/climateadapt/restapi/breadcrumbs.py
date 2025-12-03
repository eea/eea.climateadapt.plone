from plone.restapi.interfaces import IPloneRestapiLayer
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Acquisition import aq_base
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.Five import BrowserView
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer
from plone.restapi.interfaces import IExpandableElement

from plone.app.layout.navigation.root import getNavigationRoot


def get_url(item):
    if not item:
        return None
    if hasattr(aq_base(item), "getURL"):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    try:
        getId = getattr(item, "getId")
    except Exception:
        return None
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
    # props = getToolByName(context, "portal_properties")
    # stp = props.site_properties
    view_action_types = []  # stp.getProperty("typesUseViewActionInListings", ())

    item_url = get_url(context)
    name = get_id(context)

    if hasattr(context, "portal_type") and context.portal_type in view_action_types:
        item_url += "/view"
        name += "/view"

    return name, item_url


@implementer(INavigationBreadcrumbs)
class CatalogNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        # request = self.request
        ct = getToolByName(context, "portal_catalog")
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        # if utils.isDefaultPage(context, request):
        #     currentPath = "/".join(utils.parent(context).getPhysicalPath())
        # else:
        currentPath = "/".join(context.getPhysicalPath())
        query["path"] = {"query": currentPath, "navtree": 1, "depth": 0}

        rawresult = ct(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()), r) for r in rawresult]
        dec_result.sort()

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]

            # Don't include it if it would be above the navigation root
            # itemPath = item.getPath()

            id, item_url = get_view_url(item)

            if hasattr(item, "nav_title") and item.nav_title:
                title = item.nav_title
            else:
                title = (utils.pretty_title_or_id(context, item),)
            data = {
                "Title": title,
                "absolute_url": item_url,
            }
            result.append(data)
        return result


@implementer(INavigationBreadcrumbs)
class PhysicalNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        if IPloneSiteRoot.providedBy(self.context):
            return (
                {
                    "absolute_url": self.context.absolute_url(),
                    "Title": utils.pretty_title_or_id(context, context),
                },
            )

        container = utils.parent(context)

        name, item_url = get_view_url(context)

        if container is None:
            if hasattr(context, "nav_title") and context.nav_title:
                title = context.nav_title
            else:
                title = (utils.pretty_title_or_id(context, context),)
            return ({"absolute_url": item_url, "Title": title},)

        # view = getMultiAdapter((container, request), name="breadcrumbs_view")
        view = CatalogNavigationBreadcrumbs(container, request)
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = "%s/%s" % (base[-1]["absolute_url"], name)

        # this has been changed from the original file:
        # https://github.com/plone/Products.CMFPlone/blob/f028b0ce60bd62f2f5be5ccb9ecb911e73a258d1/Products/CMFPlone/browser/navigation.py
        # if not utils.isDefaultPage(context, request):
        if hasattr(context, "nav_title") and context.nav_title:
            title = context.nav_title
        else:
            title = (utils.pretty_title_or_id(context, context),)
        base += ({"absolute_url": item_url, "Title": title},)

        return base


@implementer(INavigationBreadcrumbs)
class NavTitleBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, "portal_catalog")
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        currentPath = "/".join(context.getPhysicalPath())
        query["path"] = {"query": currentPath, "navtree": 1, "depth": 0}

        rawresult = catalog(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()), r) for r in rawresult]
        dec_result.sort()

        rootPath = getNavigationRoot(context)

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]

            # Don't include it if it would be above the navigation root
            itemPath = item.getPath()
            if rootPath.startswith(itemPath):
                continue

            cid, item_url = get_view_url(item)
            if hasattr(item, "nav_title") and item.nav_title:
                title = item.nav_title
            else:
                title = (utils.pretty_title_or_id(context, item),)
            data = {
                "Title": title,
                "absolute_url": item_url,
            }
            result.append(data)
        return result


@implementer(IExpandableElement)
@adapter(Interface, IPloneRestapiLayer)
class PhysicalBreadcrumbs:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "physical-breadcrumbs": {
                "@id": "%s/@physical-breadcrumbs" % self.context.absolute_url()
            }
        }
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        breadcrumbs_view = PhysicalNavigationBreadcrumbs(self.context, self.request)
        items = []
        for crumb in breadcrumbs_view.breadcrumbs():
            item = {
                "title": crumb["Title"],
                "@id": crumb["absolute_url"],
            }
            if crumb.get("nav_title", False):
                item.update({"title": crumb["nav_title"]})

            items.append(item)

        result["physical-breadcrumbs"]["items"] = items
        result["physical-breadcrumbs"]["root"] = (
            portal_state.navigation_root().absolute_url()
        )

        return result


@implementer(IExpandableElement)
@adapter(Interface, IPloneRestapiLayer)
class Breadcrumbs:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "breadcrumbs": {"@id": "%s/@breadcrumbs" % self.context.absolute_url()}
        }
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        breadcrumbs_view = getMultiAdapter(
            (self.context, self.request), name="breadcrumbs_view"
        )

        items = []
        breadcrumbs_view = NavTitleBreadcrumbs(self.context, self.request)
        for crumb in breadcrumbs_view.breadcrumbs():
            item = {
                "title": crumb["Title"],
                "@id": crumb["absolute_url"],
            }
            if crumb.get("nav_title", False):
                item.update({"title": crumb["nav_title"]})

            items.append(item)

        result["breadcrumbs"]["items"] = items
        result["breadcrumbs"]["root"] = portal_state.navigation_root().absolute_url()

        return result


class PhysicalBreadcrumbsGet(Service):
    def reply(self):
        breadcrumbs = PhysicalBreadcrumbs(self.context, self.request)
        return breadcrumbs(expand=True)["physical-breadcrumbs"]
