#from plone.api import portal
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import PathBarViewlet as BasePathBarViewlet
from plone.app.layout.viewlets.common import SearchBoxViewlet as BaseSearchViewlet
from zope.component import getMultiAdapter


class SharePageSubMenuViewlet(ViewletBase):
    index = ViewPageTemplateFile("pt/viewlet_sharepage_submenu.pt")

    def update(self):
        super(SharePageSubMenuViewlet, self).update()
        self.base_url = '/'.join((self.context.portal_url(), 'share-your-info'))


class SearchBoxViewlet(BaseSearchViewlet):
    index = ViewPageTemplateFile('pt/searchbox.pt')


class PathBarViewlet(BasePathBarViewlet):
    """ Override to hide the breadcrumbs on the frontpage
    """

    render = ViewPageTemplateFile('pt/breadcrumbs.pt')

    def render(self):
        if not self.context.id == 'frontpage':
            return super(PathBarViewlet, self).render()

        if IPloneSiteRoot.providedBy(self.context.aq_parent):
            return ''

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        self.navigation_root_url = portal_state.navigation_root_url()

        self.is_rtl = portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()
