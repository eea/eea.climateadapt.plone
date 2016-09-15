"""
Various page overrides
"""
from plone.app.contentmenu.menu import DisplaySubMenuItem as DSMI
from plone.app.content.browser.interfaces import IContentsPage
from plone.memoize.instance import memoize
from Products.CMFPlone import utils


class DisplaySubMenuItem(DSMI):
    """ Override because we have covers with id 'index_html' and we want to
    be able to choose the display template for them
    """

    @memoize
    def disabled(self):
        if IContentsPage.providedBy(self.request):
            return True
        context = self.context
        if self.context_state.is_default_page():
            context = utils.parent(context)
        if not getattr(context, 'isPrincipiaFolderish', False):
            return False
        # By default an index_html signals disabled Display Menu, we don't want
        # that, so we return False, not disabled, by default
        elif 'index_html' in context:
            return False
        else:
            return False
