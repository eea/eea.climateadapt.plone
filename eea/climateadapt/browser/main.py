""" Controllers
"""
from Products.Five.browser import BrowserView
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class FullWidthContentTypes(BrowserView):
    """ Fullwidth body class content-types
    """

    def __init__(self, context, request):
        """ init
        """
        super(FullWidthContentTypes, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        """ boolean if fullwidth class should be enabled for given content-type
        """
        fullwidth_ctypes = self.get_full_registry() or []
        return self.context.portal_type in fullwidth_ctypes

    @memoize
    def get_full_registry(self):
        """ content registry cache
        """
        registry = getUtility(IRegistry)
        return registry.get('eea.climateadapt.interfaces.'
                            'ICCAContentTypesSettings.fullwidthFor')
