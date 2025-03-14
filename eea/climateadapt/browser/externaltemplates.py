import json
from plone import api
from plone.api import portal
from plone.app.theming.interfaces import IThemeSettings
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from eea.climateadapt.interfaces import IGoogleAnalyticsAPI

class ExternalTemplateHeader(BrowserView):

    def theme_base_url(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IThemeSettings, False)
        portal = api.portal.get()
        base_url = portal.absolute_url()

        return base_url + '/++theme++' + settings.currentTheme + '/'

    def theme_base(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IThemeSettings, False)

        return '/++theme++' + settings.currentTheme + '/'

    def pp(self, v):
        import pprint

        return pprint.pprint(v)

    def menu(self):
        try:
            ptool = getToolByName(self.context,
                                  'portal_properties')['site_properties']

            return _extract_menu(ptool.getProperty('main_navigation_menu'))
        except Exception as e:
            logger.exception("Error while rendering navigation menu: %s", e)

            return _extract_menu(DEFAULT_MENU)

    def getanalyticsid(self):
        site = portal.get()
        registry = getUtility(IRegistry, context=site)
        s = registry.forInterface(IGoogleAnalyticsAPI)

        return s.analytics_tracking_id