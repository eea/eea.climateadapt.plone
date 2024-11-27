""" Views useful for the health website functionality
"""

import logging
import re

from eea.climateadapt.browser.externaltemplates import ExternalTemplateHeader
from Products.CMFCore.utils import getToolByName
# from eea.climateadapt.translation.utils import get_current_language

from .site import _extract_menu

# from zope.component.hooks import getSite
# from Products.Five.browser import BrowserView

LINKER = re.compile("(?P<icon>\[.+?\])(?P<label>.+)")

logger = logging.getLogger("eea.climateadapt")

# NOTICE: you don't have to edit the menu here. This is a fallback, the menu
# is rendered live, from information stored in the portal. Use to edit:
# http://climate-adapt.eea.europa.eu/@@edit-health-navigation-menu
DEFAULT_MENU = """
About
    About the Observatory     /observatory/About/about-the-observatory/

Policy context
    European Policy Framework
        - EU adaptation policy /observatory/policy-context/european-policy-framework/eu-adaptation-policy
        - EU health policy    /observatory/policy-context/european-policy-framework/eu-health-policy
        - European Environment and Health Process (WHO) /observatory/policy-context/european-policy-framework/eu-environment-health-process-WHO
    Country Profiles /observatory/policy-context/country-profiles

Evidence on climate change and health
    Health effects
        -Heat and health
        -Vector-borne diseases
        -Water- and food-borne diseases
        -Air pollution
        -Wildfire
        -Flooding
    Indicators                      /observatory/evidence/indicators_intro
    Projections and tools
        -European health service
        -European climate data explorer
        -Vibrio map viewer                  /observatory/evidence/projections-and-tools/vibrio-map-viewer
    Health warning systems
        -European warning systems
        -National and sub-national warning systems

Resource catalogue      /observatory/catalogue/
    Complete catalogue      /observatory/catalogue/

Publications and outreach
    Observatory publications
        -Policy briefing
        -Annual reports
        -Newsletter
        -Story maps
    News
        -News and events
    Capacity building
        -Webinars
        -Training
"""


class Navbar(ExternalTemplateHeader):
    """The health seaction navbar"""

    def pp(self, v):
        import pprint

        return pprint.pprint(v)

    def menu(self):
        tool = getToolByName(self.context, "translation_service")
        # TODO get current language
        # current_language = get_current_language(self.context, self.request)
        current_language = "en"

        ptool = getToolByName(self.context, "portal_properties")["site_properties"]
        value = ptool.getProperty("health_navigation_menu") or DEFAULT_MENU
        site_url = self.context.portal_url()
        return _extract_menu(value, tool, None, current_language)

    def menu_site(self):
        menus = self.menu()
        return menus

    def menu_help(self):
        menus = self.menu()
        return menus[-1]
