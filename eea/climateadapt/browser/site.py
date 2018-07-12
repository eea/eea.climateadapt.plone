""" Views useful for the entire website functionality
"""

import logging
import re

from eea.climateadapt.browser.externaltemplates import ExternalTemplateHeader
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

LINKER = re.compile('(?P<icon>\[.+?\])(?P<label>.+)')

logger = logging.getLogger('eea.climateadapt')

# NOTICE: you don't have to edit the menu here. This is a fallback, the menu
# is rendered live, from information stored in the portal. Use to edit:
# http://climate-adapt.eea.europa.eu/@@edit-navigation-menu
DEFAULT_MENU = """
About        /about

Search the database         /data-and-downloads

EU policy                          /eu-adaptation-policy
    EU policy - introduction       /eu-adaptation-policy
    EU Adaptation Strategy         /eu-adaptation-policy/strategy
    EU mainstreaming in sector policies   /eu-adaptation-policy/mainstreaming
        -EU mainstreaming in sector policies - introduction   /eu-adaptation-policy/mainstreaming
        -Agriculture                   /eu-adaptation-policy/mainstreaming/agriculture
        -Forestry                      /eu-adaptation-policy/mainstreaming/forestry
        -Biodiversity                  /eu-adaptation-policy/mainstreaming/biodiversity
        -Coastal areas                 /eu-adaptation-policy/mainstreaming/coastal-areas
        -Disaster risk reduction       /eu-adaptation-policy/mainstreaming/disaster-risk-reduction
        -Financial                     /eu-adaptation-policy/mainstreaming/financial
        -Buildings                     /eu-adaptation-policy/mainstreaming/buildings
        -Energy                        /eu-adaptation-policy/mainstreaming/energy
        -Transport                     /eu-adaptation-policy/mainstreaming/transport
        -Health                        /eu-adaptation-policy/mainstreaming/health
        -Water management              /eu-adaptation-policy/mainstreaming/water-management
        -Marine and fisheries          /eu-adaptation-policy/mainstreaming/marine-and-fisheries
    EU funding of adaptation       /eu-adaptation-policy/funding
    Mayors Adapt                   /eu-adaptation-policy/mayors-adapt
        -Mayors Adapt - introduction  /eu-adaptation-policy/mayors-adapt
        -Register your City         /eu-adaptation-policy/mayors-adapt/register
        -City Profiles              /eu-adaptation-policy/mayors-adapt/city-profiles

Countries, regions, cities         /countries-regions
    Countries, regions, cities - introduction       /countries-regions
    Transnational regions          /countries-regions/transnational-regions
        -Transnational regions - Introduction         /countries-regions/transnational-regions
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
    Country Information            /countries-regions/countries

Knowledge               /knowledge
    Knowledge - introduction       /knowledge
    Adaptation information         /knowledge/adaptation-information
        -Adaptation information - introduction  /knowledge/adaptation-information
        -Observations and scenarios    /knowledge/adaptation-information/observations-and-scenarios
        -Vulnerabilities and risks     /knowledge/adaptation-information/vulnerabilities-and-risks
        -Adaptation options            /knowledge/adaptation-information/adaptation-measures
        -Adaptation strategies         /knowledge/adaptation-information/adaptation-strategies
        -Research projects             /knowledge/adaptation-information/research-projects
    ---
    Tools                          /knowledge/tools
        -Tools - introduction          /knowledge/tools
        -Adaptation Support Tool       /knowledge/tools/adaptation-support-tool
        -Case study search tool        /knowledge/tools/sat
        -Uncertainty guidance          /knowledge/tools/uncertainty-guidance
        -Map viewer                    /knowledge/tools/map-viewer
        -Urban adaptation support tool    /knowledge/tools/urban-ast/step-0-0
        -Urban vulnerability Map book     /knowledge/tools/urban-adaptation/introduction
        -Guidelines for project managers  /knowledge/tools/guidelines-for-project-managers
        -Time series tool                 /knowledge/tools/time-series-tool
        -Additional Tools                 /knowledge/tools/additional-tools

Network                 /network
    Network - introduction  /network
    Organisations           /network/organisations
    Global Platforms        /network/international

Help                        /help
    Help - introduction     /help
    Glossary                /help/glossary
    Tutorial Videos         /help/tutorial-videos
    FAQ for users           /help/faq
    Share your info         /help/share-your-info
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

    def _get_list_item(self, line):
        item = self._make_section()
        icon = ''
        label, link = line.split('/', 1)
        match = LINKER.match(label)

        if match:
            icon = match.group('icon')
            label = match.group('label').replace('[', '').replace(']', '')

        item.update({
                'icon': icon.strip(),
                'label': label.strip(),
                'link': link.strip(),
            })

        return item

    def _make_section(self,):
        return {
            'label': '',
            'link': '',
            'icon': '',
            'children': [],
        }

    def parse(self, text):
        value = text.strip()
        lines = value.split('\n')
        lines = [l.strip() for l in lines]

        # text = text.strip()
        # self.lines = text.split('\n')

        self.reset()
        self.out = []

        # import pdb; pdb.set_trace()

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
        if not self.c_column:      # this is a main section
            item['children'] = [[]]    # prepare the columns
            self.c_column = item
        else:
            self.c_group = item
            self.c_column['children'][-1].append(self.c_group)

    def handle_SUBITEM(self, item):
        self.c_group['children'].append(item)

    def handle_SECTION_SEPARATOR(self, payload):
        self.c_column['children'].append([])
        # self.c_column['children'].append(self.c_subsection)

    def reset(self):
        self.c_column = None

        # self.current_section = self._make_section()
        # self.current_subsection = []
        # # self.current_section['children'].append(self.current_subsection)
        # self.current_group = None


def _extract_menu(value):
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
    parser = MenuParser()
    result = parser.parse(value)

    # for s in split_sections(lines):
    #     s = process_section(s)
    #     result.append(s)
    # for line in lines:
    #     line = line.strip()
    #
    #     # new section (line is empty)
    #
    #     if (not line) and column[sections]:
    #         result.append(column)
    #         column = make_column()
    #
    #         continue
    #
    #     # new section
    #
    #     if line:        #  and (not this_section[-1])
    #         if '/' not in line:
    #             raise ValueError("No link in menu entry: %s" % line)
    #         label, link = line.split('/', 1)
    #         this_section[-1] = [label.strip(), link.strip(), []]
    #
    #         continue
    #
    #     # link inside section
    #
    #     if line and this_section and line[0] != '-':
    #         if '/' not in line:
    #             raise ValueError("No link in menu entry")
    #         label, link = line.split('/', 1)
    #         this_section[2].append((label.strip(), link.strip(), []))
    #
    #         continue
    #
    #     # link inside subsection
    #
    #     if line and this_section and line[0] == '-':
    #         if '/' not in line:
    #             raise ValueError("No link in menu entry")
    #         label, link = line.split('/', 1)
    #         this_section[2][-1][2].append((label.strip()[1:], link.strip()))
    #
    # if this_section:
    #     result.append(this_section)
    #

    return result


class Navbar(BrowserView, ExternalTemplateHeader):
    """ The global site navbar
    """

    def pp(self, v):
        import pprint

        return pprint.pprint(v)

    def menu(self):
        try:
            ptool = getToolByName(self.context,
                                  'portal_properties')['site_properties']

            return _extract_menu(ptool.getProperty('main_navigation_menu'))
        except Exception, e:
            logger.exception("Error while rendering navigation menu: %s", e)

            return _extract_menu(DEFAULT_MENU)
