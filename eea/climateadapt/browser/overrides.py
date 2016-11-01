"""
Various page overrides
"""
from plone.app.contentmenu.menu import DisplaySubMenuItem as DSMI
from plone.app.content.browser.interfaces import IContentsPage
from plone.memoize.instance import memoize
from Products.CMFPlone import utils

from plone.app.widgets.dx import RichTextWidget
from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer
from z3c.form.util import getSpecification
from plone.app.contenttypes.behaviors.richtext import IRichText  # noqa
from z3c.form.interfaces import IFormLayer
from plone.app.widgets.interfaces import IWidgetsLayer


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


class OverrideRichText (RichTextWidget):
    """ Richtext field override for tinymce tabs plugin """

    def _base_args(self):
        # Get options
        args = super(OverrideRichText, self)._base_args()

        # Get tinymce options
        tinyoptions = args['pattern_options']['tiny']
        buttons = 'tabs tabsDelete tabsItemDelete tabsItemInsertAfter tabsItemInsertBefore  '
        toolbar = tinyoptions['toolbar']
        plugins = tinyoptions['plugins']

        # Modify toolbar
        toolbar = toolbar.split('|')
        toolbar[5] = toolbar[5] + buttons
        toolbar = '|'.join(toolbar)

        # Override
        args['pattern_options']['tiny']['theme_advanced_buttons3'] = buttons
        args['pattern_options']['tiny']['toolbar'] = toolbar
        args['pattern_options']['tiny']['plugins'].append('tabs')
        args['pattern_options']['tiny']['plugins'].remove('contextmenu')

        return args

    def render(self):
        return super(OverrideRichText, self).render()


@adapter(getSpecification(IRichText['text']), IWidgetsLayer)
@implementer(IFieldWidget)
def RichTextFieldWidget(field, request):
    return FieldWidget(field, OverrideRichText(request))


@adapter(getSpecification(IRichText['text']), IFormLayer)
@implementer(IFieldWidget)
def RichTextFieldWidgett(field, request):
    return FieldWidget(field, OverrideRichText(request))
