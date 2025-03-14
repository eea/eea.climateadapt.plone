""" Views useful for the entire website functionality
"""

import logging
import re

from zope.component.hooks import getSite
#from plone.app.multilingual.manager import TranslationManager

from eea.climateadapt.browser.externaltemplates import ExternalTemplateHeader
# from eea.climateadapt.translation.utils import get_current_language
from Products.CMFCore.utils import getToolByName

# from Products.Five.browser import BrowserView

LINKER = re.compile('(?P<icon>\[.+?\])(?P<label>.+)')

logger = logging.getLogger('eea.climateadapt')

# NOTICE: you don't have to edit the menu here. This is a fallback, the menu
# is rendered live, from information stored in the portal. Use to edit:
# http://climate-adapt.eea.europa.eu/@@edit-navigation-menu
DEFAULT_MENU = """
EU policy                                    /eu-adaptation-policy
    EU ADAPTATION POLICY                     /eu-adaptation-policy
        -EU Adaptation Strategy              /eu-adaptation-policy/strategy
        -EU Reporting on Adaptation(MMR)     /eu-adaptation-policy/reporting
        -EU Covenant of Mayors               /eu-adaptation-policy/covenant-of-mayors
        -EU funding of adaptation            /eu-adaptation-policy/funding
    ---
    EU SECTOR POLICIES                       /eu-adaptation-policy/sector-policies
        -Agriculture                         /eu-adaptation-policy/sector-policies/agriculture
        -Biodiversity                        /eu-adaptation-policy/sector-policies/biodiversity
        -Coastal areas                       /eu-adaptation-policy/sector-policies/coastal-areas
        -Forestry                            /eu-adaptation-policy/sector-policies/forestry
        -Water management                    /eu-adaptation-policy/sector-policies/water-management
        -Marine and fisheries                /eu-adaptation-policy/sector-policies/marine-and-fisheries
        -Ecosystem-based approaches(GI)      /eu-adaptation-policy/sector-policies/ecosystem
        -Disaster risk reduction             /eu-adaptation-policy/sector-policies/disaster-risk-reduction
        -Financial                           /eu-adaptation-policy/sector-policies/financial
        -Buildings                           /eu-adaptation-policy/sector-policies/buildings
        -Energy                              /eu-adaptation-policy/sector-policies/energy
        -Transport                           /eu-adaptation-policy/sector-policies/transport
        -Health                              /eu-adaptation-policy/sector-policies/health
    OTHER EU POLICIES                        /eu-adaptation-policy
        -EU Regional policy                  /eu-adaptation-policy
        -EU Neighbourhood policy             /eu-adaptation-policy

Countries, Transnational regions, Cities              /countries-regions
Country Profiles                                      /countries-regions/countries
Transnational regions                                 /countries-regions/transnational-regions
        -Adriatic-Ionian                              /countries-regions/transnational-regions/adriatic-ionian
        -Alpine Space                                 /countries-regions/transnational-regions/alpine-space
        -Atlantic Area                                /countries-regions/transnational-regions/atlantic-area
        -Balkan-Mediterranean                         /countries-regions/transnational-regions/balkan-mediterranean
        -Baltic Sea                                   /countries-regions/transnational-regions/baltic-sea-region
        -Central Europe                               /countries-regions/transnational-regions/central-europe
        -Danube                                       /countries-regions/transnational-regions/danube
        -Mediterranean                                /countries-regions/transnational-regions/mediterranean
        -North Sea                                    /countries-regions/transnational-regions/north-sea
        -North West Europe                            /countries-regions/transnational-regions/north-west-europe
        -Northern Periphery and Arctic                /countries-regions/transnational-regions/northern-periphery
        -South West Europe                            /countries-regions/transnational-regions/south-west-europe
        -Other regions                                /countries-regions/transnational-regions/other-regions
Cities and towns               /countries-regions/cities

Knowledge                                                     /knowledge
    TOPICS                                                    /knowledge
        -Impacts,Risks and Vulnerabilities                    /knowledge/adaptation-information/vulnerabilities-and-risks
        -Adaptation options                                   /knowledge/adaptation-information/adaptation-measures
        -Uncertainty guidance                                 /knowledge/tools/uncertainty-guidance
        -MRE                                                  /knowledge
        -EU vulnerability to outside Europe climate impacts   /knowledge
    DATA AND INDICATORS                                       /knowledge
        -Climate services(>C3S)                               /knowledge/adaptation-information/climate-services/
        -Indicators in C-A                                    /knowledge
    RESEARCH                                                  /knowledge
        -Research projects                                    /knowledge/adaptation-information/research-projects
    ---
    TOOLS                                                     /knowledge/tools
        -Adaptation Support Tool                              /knowledge/tools/adaptation-support-tool
        -Urban adaptation support tool                        /knowledge/tools/urban-ast/step-0-0
        -Urban vulnerability Map book                         /knowledge/tools/urban-adaptation/introduction
        -Economic tools                                       /knowledge/tools/additional-tools
    PRACTICE                                                  /knowledge
        -Case studies                                         /knowledge/tools/sat
        -Case studies with map viewer                         /knowledge/tools/map-viewer
        -LIFE projects                                        /knowledge
        -INTERREG projects                                    /knowledge
        [<icon class="fa fa-database">]Search the database    /data-and-downloads

About                    /about
    Description          /about
    Visual site-map      /about/visual-site-map
    Profile of C-A       /about/profile

C-A Database            /data-and-downloads

Networks                /network
    Organisations       /network/organisations

Help                                        /help
    Glossary                                /help/glossary
    FAQ users                               /help/faq
    FAQ providers                           /help/providers
    Guidance to search function             /help/guidance
    Guidance for different types of users   /help/guidance
    Tutorial Videos                         /help/tutorial-videos
    C-A use cases                           /help/use-cases
    Share your info                         /help/share-your-info
    """


# def split_sections(lines):
#     """ Group the list of lines in a list of sections
#     """
#     result = [[]]
#
#     for line in lines:
#         if line:
#             result[-1].append(line)
#         else:
#             result.append([])
#
#     return result

# def get_subsections(rest):
#     """ Subsections are the columns in the menu
#     """
#
#     result = [[]]
#
#     for line in lines:
#         if not line.startswith('---'):
#             result[-1].append(line)
#         else:
#             result.append([])
#
#     return process_subsections(result)
#
#
# def split_groups():
#     pass
#
#
# def process_subsections(sections):
#     # get_list_item(line)
#     res = []
#
#     groups = [[]]
#
#     for section in sections:
#         for line in section:
#             if not line.startswith('-'):
#                 result[-1].append(line)
#             else:
#                 result.append([])
#         groups = []
#
#     return result
#
#
# def process_section(lines):
#     """ A section is a whole global section, a main entry in the menu
#     """
#     item['children'] = get_subsections(rest)
#
#     return item


class MenuParser:
    EMPTY_LINE = 'EMPTY_LINE'
    SECTION_SEPARATOR = 'SECTION_SEPARATOR'
    ITEM = 'ITEM'
    SUBITEM = 'SUBITEM'
    site_url = None
    translation_tool = None
    translation_language = 'en'

    def __init__(self, site_url):
        self.site_url = site_url

    def _get_list_item(self, line):
        item = self._make_section()
        icon = ''
        info = line.split('/', 1)

        if len(info) == 2:
            label, link = info
        else:
            label = info[0]
            link = None
        match = LINKER.match(label)

        if match:
            icon = match.group('icon').replace('[', '').replace(']', '')
            label = match.group('label').replace('[', '').replace(']', '')

        if self.translation_tool:
            label = self.translation_tool.translate(label.strip(),
                        domain="eea.climateadapt.menu",
                        target_language=self.translation_language);

        if link:
            if "++aq++" in link:
                link = link.replace("/en/observatory", "/"+self.translation_language+"/observatory")
                link = link.replace("/++aq++en/", "/++aq++"+self.translation_language+"/")
            if link.endswith('catalogue/') and self.translation_language != 'en':
                link = link + '?lang=' + self.translation_language
            if link.endswith('data-and-downloads'):
                link = link + '/?lang=' + self.translation_language
            if link.endswith('data-and-downloads/'):
                link = link + '?lang=' + self.translation_language

        item.update({
            'icon': icon.strip() + '</icon>',
            'label': label.strip(),
            'link': link and (self.site_url + '/'
                    + self.translation_language + '/' + link.strip()) or None,
        })

        return item

    def _make_section(self,):
        return {
            'label': '',
            'link': '',
            'icon': '',
            'children': [],
        }

    def parse(self, text, translation_tool = None, current_language = 'en'):
        self.translation_tool = translation_tool
        self.translation_language = current_language

        value = text.strip()
        lines = value.split('\n')
        lines = [l.strip() for l in lines]

        self.reset()
        self.out = []

        for line in lines:
            self.process(line)

        # handle end of lines
        self.out.append(self.c_column)

        return self.out

    def process(self, line):
        token, payload = self.tokenize(line)
        handler = getattr(self, 'handle_' + token)
        handler(payload)

    def tokenize(self, line):
        line = line.strip()

        if not line:
            return (self.EMPTY_LINE, '')

        if line == '---':
            return (self.SECTION_SEPARATOR, '')

        token = self.ITEM

        if line.startswith('-'):
            token = self.SUBITEM
            line = line[1:]

        item = self._get_list_item(line)

        return (token, item)

    def handle_EMPTY_LINE(self, payload):
        # on empty lines, add the section and reset the state machine

        self.out.append(self.c_column)
        self.c_column = None
        self.reset()

    def handle_ITEM(self, item):
        if not self.c_column:           # this is a main section
            item['children'] = [[]]     # prepare the columns
            self.c_column = item
        else:
            self.c_group = item
            self.c_column['children'][-1].append(self.c_group)

    def handle_SUBITEM(self, item):
        self.c_group['children'].append(item)

    def handle_SECTION_SEPARATOR(self, payload):
        self.c_column['children'].append([])

    def reset(self):
        self.c_column = None


def _extract_menu(value, translation_tool = None, site_url=None, language = 'en'):
    """ Construct the data for the menu.

    Terminology in the menu:
    |-----------------------------------------------------------|
    | <section>        |       <section>        |     <section> |
    |-----------------------------------------------------------|
    | <subsection>   <subsection>   |                           |
    | <group A>      <group C>      |                           |
    | <link 1>       <link 1>       |                           |
    | <link 2>       <link 2>       |                           |
    | ...                           |                           |
    | <group B>                     |                           |
    | <link 3>                      |                           |
    | <link 4>                      |                           |
    |-----------------------------------------------------------|
    """

    if not site_url:
        site_url = getSite().absolute_url()
    parser = MenuParser(site_url)
    result = parser.parse(value, translation_tool, language)
    return result


class Navbar(ExternalTemplateHeader):
    """ The global site navbar
    """

    def pp(self, v):
        import pprint

        return pprint.pprint(v)

    def menu(self):
        tool = getToolByName(self.context, "translation_service")
        try:
            ptool = getToolByName(self.context,
                                  'portal_properties')['site_properties']

            # TODO fix current_language
            # current_language = get_current_language(self.context, self.request)
            current_language = 'en'
            sections = _extract_menu(ptool.getProperty('main_navigation_menu'),
                            tool, None, current_language)
            for idx in range(len(sections)):
                if not sections[idx]:
                    sections.pop(idx)

            return sections
        except Exception as e:
            logger.exception("Error while rendering navigation menu: %s", e)

            site_url = self.context.portal_url()
            return _extract_menu(DEFAULT_MENU, tool, site_url)

    def menu_site(self):
        menus = self.menu()
        return menus[0:-1]

    def menu_help(self):
        menus = self.menu()
        if len(menus):
            return menus[-1]
        return []

    def translate_url(self, url):
        lang_independent_urls = [
            #"privacy-and-legal-notice", "/sitemap"
            "user-dashboard", "eea-disclaimer",
            ]
        for lang_independent_url in lang_independent_urls:
            if url.endswith(lang_independent_url):
                return url

        # TODO fix current_language
        # current_language = get_current_language(self.context, self.request)
        current_language = 'en'
        #logger.info("Will translate LANG %s, URL: %s", current_language, url)
        if '/' == url:
            url = "/?set_language="+current_language
            #logger.exception("Translate URL1: %s", url)
            return url

        if url.endswith('/catalogue/'):
            if current_language == 'en':
                return url
            url = url + '?lang=' + current_language
            url = url.replace('/en/','/'+current_language+'/')
            #logger.info("Translate URL2: %s", url)
            return url
        if url.endswith('/data-and-downloads/'):
            if current_language == 'en':
                return url
            url = url + '?lang=' + current_language
            url = url.replace('/en/','/'+current_language+'/')
            #logger.info("Translate URL3: %s", url)
            return url

        site = getSite()
        try:
            if '/'+current_language+'/' in url:
                return url

            '''
            Replace the link with current language, tooks to much time and
            external templates for search app are not created for all languages
            '''
            url = url.replace('/en/', '/'+current_language+'/');
            return url

            #obj = site.unrestrictedTraverse('/cca' + url)
            #translations = TranslationManager(obj).get_translations()
            #if current_language in translations:
            #    trans_obj = translations[current_language]

            #    url = trans_obj.absolute_url()
                #logger.info("Translate URL4: %s", trans_obj.absolute_url())
            #else:
            #    logger.info("Translate fail URL4.1: [%s]", url)
        except Exception as e:
            logger.exception("Translate error: %s for %s", e, url)
            #logger.info("Translate URL5: %s", url)

        return url
