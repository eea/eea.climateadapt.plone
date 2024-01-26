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
from zope.interface import implements
from plone.restapi.interfaces import IExpandableElement

# from plone.app.layout.navigation.root import getNavigationRoot


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
    getId = getattr(item, "getId")
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
    props = getToolByName(context, "portal_properties")
    stp = props.site_properties
    view_action_types = stp.getProperty("typesUseViewActionInListings", ())

    item_url = get_url(context)
    name = get_id(context)

    if hasattr(context, "portal_type") and context.portal_type in view_action_types:
        item_url += "/view"
        name += "/view"

    return name, item_url


class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        name, item_url = get_view_url(context)

        if container is None:
            return (
                {
                    "absolute_url": item_url,
                    "Title": utils.pretty_title_or_id(context, context),
                },
            )

        view = getMultiAdapter((container, request), name="breadcrumbs_view")
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = "%s/%s" % (base[-1]["absolute_url"], name)

        # this has been changed from the original file:
        # https://github.com/plone/Products.CMFPlone/blob/f028b0ce60bd62f2f5be5ccb9ecb911e73a258d1/Products/CMFPlone/browser/navigation.py
        if not utils.isDefaultPage(context, request):
            base += (
                {
                    "absolute_url": item_url,
                    "Title": utils.pretty_title_or_id(context, context),
                },
            )

        return base


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class PhysicalBreadcrumbs:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "physical_breadcrumbs": {
                "@id": f"{self.context.absolute_url()}/@physical_breadcrumbs"
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

        result["breadcrumbs"]["items"] = items
        result["breadcrumbs"]["root"] = portal_state.navigation_root().absolute_url()
        return result


class PhysicalBreadcrumbsGet(Service):
    def reply(self):
        breadcrumbs = PhysicalBreadcrumbs(self.context, self.request)
        return breadcrumbs(expand=True)["breadcrumbs"]
