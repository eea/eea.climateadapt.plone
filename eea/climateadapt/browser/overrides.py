"""
Various page overrides
"""
from plone.app.contentmenu.menu import DisplaySubMenuItem as DSMI
from plone.app.content.browser.interfaces import IContentsPage
from plone.memoize.instance import memoize
from Products.CMFPlone import utils


class DisplaySubMenuItem(DSMI):

    @memoize
    def disabled(self):
        if IContentsPage.providedBy(self.request):
            return True
        context = self.context
        if self.context_state.is_default_page():
            context = utils.parent(context)
        if not getattr(context, 'isPrincipiaFolderish', False):
            return False
        # elif 'index_html' not in context:
        #     return False
        # elif 'index_html' in context:
        #     return False
        else:
            return False
