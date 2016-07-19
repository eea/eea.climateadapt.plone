from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
import logging

logger = logging.getLogger('eea.climateadapt')


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


def _extract_menu(value):
    lines = value.split('\n')
    sections = []
    this_section = None

    # TODO: use x.split('/', 1) instead of find
    for line in lines:
        line = line.strip()

        # empty lines at beginning of docstring
        if not line and this_section is None:
            continue

        # new section
        if not line and this_section:
            sections.append(this_section)
            this_section = None
            continue

        # new section
        if line and this_section is None:
            if not '/' in line:
                raise ValueError("No link in menu entry: %s" % line)
            lpos = line.find('/')
            label, link = line[:lpos].strip(), line[lpos:].strip()
            this_section = [label, link, []]
            continue

        # link inside section
        if line and this_section and line[0] != '-':
            if not '/' in line:
                raise ValueError("No link in menu entry")
            lpos = line.find('/')
            label, link = line[:lpos].strip(), line[lpos:].strip()
            this_section[2].append((label, link, []))
            continue

        # link inside subsection
        if line and this_section and line[0] == '-':
            if not '/' in line:
                raise ValueError("No link in menu entry")
            lpos = line.find('/')
            label, link = line[1:lpos].strip(), line[lpos:].strip()
            this_section[2][-1][2].append((label, link))

    if this_section:
        sections.append(this_section)

    return sections


class Navbar(BrowserView):
    """ The global site navbar
    """

    def menu(self):
        try:
            ptool = getToolByName(self.context,
                                'portal_properties')['site_properties']
            return _extract_menu(ptool.getProperty('main_navigation_menu'))
        except Exception, e:
            logger.exception("Error while rendering navigation menu: %s", e)
            return _extract_menu(DEFAULT_MENU)
