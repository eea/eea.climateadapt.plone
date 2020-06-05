""" Views useful for the health website functionality
"""

import logging
import re

from eea.climateadapt.browser.externaltemplates import ExternalTemplateHeader
from Products.CMFCore.utils import getToolByName

from .site import _extract_menu

# from zope.component.hooks import getSite

# from Products.Five.browser import BrowserView

LINKER = re.compile('(?P<icon>\[.+?\])(?P<label>.+)')

logger = logging.getLogger('eea.climateadapt')

# NOTICE: you don't have to edit the menu here. This is a fallback, the menu
# is rendered live, from information stored in the portal. Use to edit:
# http://climate-adapt.eea.europa.eu/@@edit-health-navigation-menu
DEFAULT_MENU = """
Background Information
    About the observatory            /about
        -Mission and objectives      /eu-adaptation-policy/strategy
        -Network                     /eu-adaptation-policy/strategy
    European Policies              /about/Outreach
    National                       /sitemap

Evidence on climate change and health
    Health impacts
        -Heat efects
        -Vectore borne diseases
        -Food and water born diseases
        -Air polution
        -Wildfire
        -Flooding
        -Etc.
    Indicators
    Projections and tools                            /a/b
        -Infectious diseas                           /a/b
        -Modelling results                           /a/b
        -European health service                     /a/b
        -European climate data explorer              /a/b
    Health warning systems
        -European warning systems                    /a/b
        -Vibrio map viewer                           /a/b
        -National and sub-national warning systems   /a/b

Resource catalogue      /health/resource-catalogue

Publications and outreach
    Publications                          /a/c
        -Policy briefing       /a/b
        -Anual reports    /a/b
        -Newsletter              /a
        -Story maps              /a
    News
        -News and events         /a
    Capacity building            /a/b/c
        -Webinars                /a/b/c
        -Training                /a/b/c
"""


class Navbar(ExternalTemplateHeader):
    """ The health seaction navbar
    """

    def pp(self, v):
        import pprint

        return pprint.pprint(v)

    def menu(self):
        ptool = getToolByName(self.context,
                              'portal_properties')['site_properties']
        value = ptool.getProperty('health_navigation_menu') or DEFAULT_MENU
        site_url = self.context.portal_url()
        return _extract_menu(value, site_url)
