from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import CatalogNavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import get_view_url
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class SharePageSubMenuViewlet(ViewletBase):

    index = ViewPageTemplateFile("pt/viewlet_sharepage_submenu.pt")

    def update(self):
        super(SharePageSubMenuViewlet, self).update()

        self.base_url = '/'.join((self.context.portal_url(), 'share-your-info'))


class FixBreadcrumbs(CatalogNavigationBreadcrumbs):
    """ We want to hide from the breadcrumbs those parent folders of covers.
    """

    # def is_parent_of_cover(self, info):
    #     brain = info['brain']
    #     obj = brain.getObject()
    #     types = set([o.portal_type for o in obj.contentValues()])
    #
    #     if 'collective.cover.content' not in types:
    #         return True
    #
    #     print "hiding ", obj
    #     return False
    #
    # def breadcrumbs(self):
    #     """ Override the breadcrumbs to retrieve full objects and to filter
    #     them based on self.is_parent_of_cover
    #     """
    #     context = aq_inner(self.context)
    #     request = self.request
    #     ct = getToolByName(context, 'portal_catalog')
    #     query = {}
    #
    #     # Check to see if the current page is a folder default view, if so
    #     # get breadcrumbs from the parent folder
    #     if utils.isDefaultPage(context, request):
    #         currentPath = '/'.join(utils.parent(context).getPhysicalPath())
    #     else:
    #         currentPath = '/'.join(context.getPhysicalPath())
    #     query['path'] = {'query': currentPath, 'navtree': 1, 'depth': 0}
    #
    #     rawresult = ct(**query)
    #
    #     # Sort items on path length
    #     dec_result = [(len(r.getPath()), r) for r in rawresult]
    #     dec_result.sort()
    #
    #     rootPath = getNavigationRoot(context)
    #
    #     # Build result dict
    #     result = []
    #     for r_tuple in dec_result:
    #         item = r_tuple[1]
    #
    #         # Don't include it if it would be above the navigation root
    #         itemPath = item.getPath()
    #         if rootPath.startswith(itemPath):
    #             continue
    #
    #         id, item_url = get_view_url(item)
    #         data = {'Title': utils.pretty_title_or_id(context, item),
    #                 'absolute_url': item_url,
    #                 'brain': item}
    #         result.append(data)
    #
    #     return [x for x in result if self.is_parent_of_cover(x)]
