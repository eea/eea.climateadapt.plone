from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import ViewletBase
from plone.app.layout.viewlets.common import SearchBoxViewlet as BaseSearchViewlet
#from plone.app.stagingbehavior.browser.info import BaselineInfoViewlet as InfoViewlet


class SharePageSubMenuViewlet(ViewletBase):
    index = ViewPageTemplateFile("pt/viewlet_sharepage_submenu.pt")

    def update(self):
        super(SharePageSubMenuViewlet, self).update()
        self.base_url = '/'.join((self.context.portal_url(), 'share-your-info'))


class SearchBoxViewlet(BaseSearchViewlet):
    index = ViewPageTemplateFile('pt/searchbox.pt')


# class BaselineInfoViewlet(InfoViewlet):
#     """ Override
#     """
#     pass

