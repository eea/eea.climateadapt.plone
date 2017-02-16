# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from collections import namedtuple
from plone.app.querystring import queryparser
from plone.app.vocabularies.catalog import CatalogVocabulary as BCV
from plone.app.vocabularies.catalog import CatalogVocabularyFactory
from plone.app.vocabularies.catalog import KeywordsVocabulary as BKV
from plone.uuid.interfaces import IUUID
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import pycountry


def generic_vocabulary(_terms, sort=True):
    """ Returns a zope vocabulary from a dict or a list
    """

    if _terms and isinstance(_terms, dict):
        _terms = dict.items()
    elif _terms and isinstance(_terms[0], basestring):
        _terms = [(x, x) for x in _terms]

    if sort:
        _terms = sorted(_terms, key=lambda x: x[0])

    def factory(context):
        return SimpleVocabulary([
            SimpleTerm(n, n.encode('utf-8'), l) for n, l in _terms
        ])

    return factory


@implementer(IVocabularyFactory)
class KeywordsVocabulary(BKV):
    def __init__(self, index):
        self.keyword_index = index


class CatalogVocabulary(BCV):

    def getTerm(self, value):
        if isinstance(value, basestring):
            # perhaps it's already a uid
            uid = value
        else:
            uid = IUUID(value)
        for term in self._terms:
            try:
                term_uid = term.value.UID
            except AttributeError:
                term_uid = term.value
            if uid == term_uid:
                return term


@implementer(IVocabularyFactory)
class AdaptationOptionsVocabulary(CatalogVocabularyFactory):

    def __call__(self, context, query=None):
        query = query or {}

        if 'criteria' not in query:
            query['criteria'] = []

        query['criteria'].append(
            {u'i': u'portal_type',
             u'o': u'plone.app.querystring.operation.selection.is',
             u'v': [u'eea.climateadapt.adaptationoption']}
        )

        parsed = {}
        if query:
            parsed = queryparser.parseFormquery(context, query['criteria'])
            if 'sort_on' in query:
                parsed['sort_on'] = query['sort_on']
            if 'sort_order' in query:
                parsed['sort_order'] = str(query['sort_order'])
        try:
            catalog = getToolByName(context, 'portal_catalog')
        except AttributeError:
            catalog = getToolByName(getSite(), 'portal_catalog')

        if parsed.get('path'):
            if parsed['path'].get('depth'):
                parsed['path']['query'].append(u'/cca/metadata/adaptation-options')
                if u'/cca' in parsed['path']['query']:
                    parsed['path']['query'].remove(u'/cca')

        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


@implementer(IVocabularyFactory)
class CCAItemsVocabulary(CatalogVocabularyFactory):

    def __call__(self, context, query=None):
        query = query or {}

        if 'criteria' not in query:
            query['criteria'] = []

        query['criteria'].append(
            {u'i': u'portal_type',
             u'o': u'plone.app.querystring.operation.selection.is',
             u'v':
             [
                 u'eea.climateadapt.adaptationoption',
                 u'eea.climateadapt.aceproject',
                 u'eea.climateadapt.casestudy',
                 u'eea.climateadapt.guidancedocument',
                 u'eea.climateadapt.indicator',
                 u'eea.climateadapt.informationportal',
                 u'eea.climateadapt.mapgraphdataset',
                 u'eea.climateadapt.organisation',
                 u'eea.climateadapt.publicationreport',
                 u'eea.climateadapt.researchproject',
                 u'eea.climateadapt.tool',
                 u'eea.climateadapt.city_profile',
                 u'Folder',
             ]}
        )

        parsed = {}
        if query:
            parsed = queryparser.parseFormquery(context, query['criteria'])
            if 'sort_on' in query:
                parsed['sort_on'] = query['sort_on']
            if 'sort_order' in query:
                parsed['sort_order'] = str(query['sort_order'])
        try:
            catalog = getToolByName(context, 'portal_catalog')
        except AttributeError:
            catalog = getToolByName(getSite(), 'portal_catalog')

        if parsed.get('path'):
            if parsed['path'].get('depth'):
                parsed['path']['query'].append(u'/cca/metadata')
                if u'/cca' in parsed['path']['query']:
                    parsed['path']['query'].remove(u'/cca')
        brains = catalog(**parsed)

        return CatalogVocabulary.fromItems(brains, context)


# changes title and buttons (what to add) in view for AceItem
# extracted from JAVA code:
_datatypes = [
    ("DOCUMENT", "Publications and reports"),
    ("INFORMATIONSOURCE", "Information portals"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("GUIDANCE", "Guidance"),
    ("TOOL", "Tools"),
    ("RESEARCHPROJECT", "Research and knowledge projects"),
    ("MEASURE", "Adaptation options"),
    ("ACTION", "Case studies"),
    ("ORGANISATION", "Organisations"),
]
aceitem_datatypes_vocabulary = generic_vocabulary(_datatypes)
alsoProvides(aceitem_datatypes_vocabulary, IVocabularyFactory)


# changes how the view for AceItem behaves (what it shows)
_storagetypes = [
    "PLAINMETADATA",
    "PROJECT",
    "MAPLAYER",
    "URL",
    "SETOFMAPS",
    "MEASURE",
]
aceitem_storagetypes_vocabulary = generic_vocabulary(_storagetypes)
alsoProvides(aceitem_storagetypes_vocabulary, IVocabularyFactory)


_sectors = [    # this is the canonical
    # ("AGRICULTURE", "Agriculture and Forest"),
    ("AGRICULTURE", "Agriculture"),
    ("FORESTRY", "Forestry"),
    ("BIODIVERSITY", "Biodiversity"),
    ("COASTAL", "Coastal areas"),
    ("DISASTERRISKREDUCTION", "Disaster Risk Reduction"),
    ("FINANCIAL", "Financial"),
    ("HEALTH", "Health"),
    # ("INFRASTRUCTURE", "Infrastructure"),
    ("URBAN", "Urban"),
    ("MARINE", "Marine and Fisheries"),
    #   ("TOURISM", "Tourism"),
    ("ENERGY", "Energy"),
    ("TRANSPORT", "Transport"),
    ("BUILDINGS", "Buildings"),
    #   ("OTHER", "Other"),
    ("WATERMANAGEMENT", "Water management"),
]
aceitem_sectors_vocabulary = generic_vocabulary(_sectors)
alsoProvides(aceitem_sectors_vocabulary, IVocabularyFactory)

_elements = [
    ("EU_POLICY", "Sector Policies"),
    ("MEASUREACTION", "Adaptation Measures and Actions"),
    ("OBSERVATIONS", "Observations and Scenarios"),
    ("PLANSTRATEGY", "Adaptation Plans and Strategies"),
    ("VULNERABILITY", "Vulnerability Assessment"),
]
aceitem_elements_vocabulary = generic_vocabulary(_elements)
alsoProvides(aceitem_elements_vocabulary, IVocabularyFactory)

# Vocabulary for faceted search "Adaptation elements"
fac_elements = [
    ("OBSERVATIONS", "Observations and Scenarios"),
    ("VULNERABILITY", "Vulnerability Assessment"),
    ("MEASUREACTION", "Adaptation Measures and Actions"),
    ("PLANSTRATEGY", "Adaptation Plans and Strategies"),
    ("EU_POLICY", "Sector Policies"),
]
faceted_elements = generic_vocabulary(fac_elements, sort=False)
alsoProvides(faceted_elements, IVocabularyFactory)

_climateimpacts = [
    ("EXTREMETEMP", "Extreme Temperatures"),
    ("WATERSCARCE", "Water Scarcity"),
    ("FLOODING", "Flooding"),
    ("SEALEVELRISE", "Sea Level Rise"),
    ("DROUGHT", "Droughts"),
    ("STORM", "Storms"),
    ("ICEANDSNOW", "Ice and Snow"),
]
aceitem_climateimpacts_vocabulary = generic_vocabulary(_climateimpacts)
alsoProvides(aceitem_climateimpacts_vocabulary, IVocabularyFactory)


_featured = [('CASEHOME', 'Feature this on the homepage'),
             ('CASESEARCH', 'Feature this on study search results page')]
aceitem_featured_vocabulary = generic_vocabulary(_featured)
alsoProvides(aceitem_featured_vocabulary, IVocabularyFactory)

_relevance = [
    ('IMPL_AS_CCA', 'Case developed and implemented as a CCA (Climate Change Adaptation) Measure.'),
    ('PARTFUND_AS_CCA', 'Case developed and implemented and partially funded as a CCA measure.'),
    ('OTHER_POL_OBJ', 'Case mainly developed and implemented because of other policy objectives, but with significant consideration of CCA aspects'),
    ]
aceitem_relevance_vocabulary = generic_vocabulary(_relevance)
alsoProvides(aceitem_relevance_vocabulary, IVocabularyFactory)

_implementationtypes = (("grey", "Technical ('grey')"),
                        ("green", "Ecological ('green')"),
                        ("soft", "Behavioural / policy ('soft')")
                        )
acemeasure_implementationtype_vocabulary = generic_vocabulary(_implementationtypes)
alsoProvides(acemeasure_implementationtype_vocabulary, IVocabularyFactory)

# Used for aceitems
european_countries = ['AD', 'AL', 'AM', 'AT', 'AZ', 'BA', 'BE', 'BG', 'BY',
                      'CH', 'RS', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
                      'FO', 'FR', 'GB', 'GE', 'GR', 'HR', 'HU', 'IE', 'IL',
                      'IS', 'IT', 'KZ', 'LI', 'LT', 'LU', 'LV', 'MC', 'MD',
                      'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI',
                      'SK', 'SM', 'TR', 'UA', 'ME']
ace_countries = [(x.alpha2, x.name) for x in pycountry.countries
                 if x.alpha2 in european_countries]
ace_countries.append(('FYROM', 'Former Yugoslav Republic of Macedonia'))
ace_countries.append(('MK', 'Republic of Macedonia'))
ace_countries.append(('XK', 'Kosovo under UN Security Council Resolution 1244/99'))
ace_countries_dict = dict(ace_countries)

ace_countries_vocabulary = generic_vocabulary(ace_countries)
alsoProvides(ace_countries_vocabulary, IVocabularyFactory)


eu_countries_selection = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                          'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU',
                          'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
                          'CH', 'TR', 'GB']

# Used for dropdowns
ace_countries_selection = [(x.alpha2, x.name) for x in pycountry.countries
                           if x.alpha2 in eu_countries_selection]

# Used for faceted search in /data-and-downloads
faceted_countries = ['AL', 'AT', 'BE', 'BG', 'BA', 'HR', 'CY', 'CZ', 'DK',
                     'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                     'LV', 'LI', 'LT', 'LU', 'MT', 'ME', 'NL', 'NO', 'PL',
                     'PT', 'RO', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR',
                     'GB']
faceted_countries = [(x.alpha2, x.name) for x in pycountry.countries
                     if x.alpha2 in faceted_countries]
faceted_countries.append(('FYROM', 'F. Y. R. O. Macedonia'))
faceted_countries.append(('XK', 'Kosovo under UN Security Council Resolution 1244/99'))

faceted_countries_dict = dict(faceted_countries)

faceted_countries_vocabulary = generic_vocabulary(faceted_countries)
alsoProvides(faceted_countries_vocabulary, IVocabularyFactory)

_measure_types = (("A", "Case study"), ("M", "Adaptation option"))
acemeasure_types = generic_vocabulary(_measure_types)
alsoProvides(acemeasure_types, IVocabularyFactory)

_cca_types = [
    ("DOCUMENT", "Publication & Report"),
    ("INFORMATIONSOURCE", "Information Portal"),
    ("GUIDANCE","Guidance Document"),
    ("TOOL", "Tool"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("RESEARCHPROJECT","Research and Knowledge Projects"),
    ("MEASURE","Adaptation Option"),
    ("ACTION", "Case Studies"),
    ("ORGANISATION", "Organisation"),
]
cca_types = generic_vocabulary(_cca_types)
alsoProvides(cca_types, IVocabularyFactory)

_a = namedtuple('_AceItemType', ['id', 'label'])
aceitem_types = [_a(*x) for x in _cca_types]

SpecialTagsVocabularyFactory = KeywordsVocabulary('special_tags')
KeywordsVocabularyFactory = KeywordsVocabulary('keywords')

_governance = [
    ("TRANS", "Transnational region (stretching across country borders)"),
    ("NAT", "National"),
    ("SNA", "Sub National Regions"),
    ("LC", "Local (e.g. city or municipal level)"),
]
governance_level = generic_vocabulary(_governance)
alsoProvides(governance_level, IVocabularyFactory)

_category = [
    ("Grey", "Grey: technological and engineering solutions aiming mainly at the protection of infrastructures or people."),
    ("Green", "Green: ecosystem-based approaches that use the multiple services of nature aiming at raising the resilience of ecosystems and their services."),
    ("Soft", "Soft: managerial, legal and policy approaches that alter human behavior and styles of governance (e.g. spatial planning and policies), including financial/fiscal instruments, such as insurance"),
]
category = generic_vocabulary(_category)
alsoProvides(category, IVocabularyFactory)

_header_level = (
    ("h1", "Header 1"),
    ("h2", "Header 2"),
    ("h3", "Header 3"),
    ("h4", "Header 4"),
    ("h5", "Header 5"),
)
rich_header_level = generic_vocabulary(_header_level)
alsoProvides(rich_header_level, IVocabularyFactory)

labels = """
acesearch-geochars-lbl-GLOBAL=Global
acesearch-geochars-lbl-EUROPE=Europe
acesearch-geochars-lbl-MACRO_TRANSNATIONAL_REGION=Macro-Transnational Regions
acesearch-geochars-lbl-BIOGRAPHICAL_REGION=Biogeographical Regions
acesearch-geochars-lbl-COUNTRIES=Countries
acesearch-geochars-lbl-SUBNATIONAL=Subnational Regions
acesearch-geochars-lbl-CITY=Municipality Name
acesearch-geochars-lbl-TRANS_MACRO_NORTHPERI=Northern Periphery
acesearch-geochars-lbl-TRANS_MACRO_BACLITC=Baltic Sea
acesearch-geochars-lbl-TRANS_MACRO_NW_EUROPE=North West Europe
acesearch-geochars-lbl-TRANS_MACRO_N_SEA=North Sea
acesearch-geochars-lbl-TRANS_MACRO_ATL_AREA=Atlantic Area
acesearch-geochars-lbl-TRANS_MACRO_ALP_SPACE=Alpine Space
acesearch-geochars-lbl-TRANS_MACRO_CEN_EUR=Central Europe
acesearch-geochars-lbl-TRANS_MACRO_SW_EUR=South West Europe
acesearch-geochars-lbl-TRANS_MACRO_MED=Mediterranean
acesearch-geochars-lbl-TRANS_MACRO_SE_EUR=South East Europe
acesearch-geochars-lbl-TRANS_MACRO_CAR_AREA=Caribbean Area
acesearch-geochars-lbl-TRANS_MACRO_MACRONESIA=Macronesia
acesearch-geochars-lbl-TRANS_MACRO_IND_OCEAN_AREA=Indian Ocean Area
acesearch-geochars-lbl-TRANS_BIO_ALPINE=Alpine
acesearch-geochars-lbl-TRANS_BIO_ATLANTIC=Atlantic
acesearch-geochars-lbl-TRANS_BIO_ARCTIC=Arctic
acesearch-geochars-lbl-TRANS_BIO_BOREAL=Boreal
acesearch-geochars-lbl-TRANS_BIO_CONTINENTAL=Continental
acesearch-geochars-lbl-TRANS_BIO_MEDIT=Mediterranean
acesearch-geochars-lbl-TRANS_BIO_PANNONIAN=Pannonian
"""

BIOREGIONS = {}

for line in filter(None, labels.split('\n')):
    first, label = line.split('=')
    name = first.split('-lbl-')[1]
    BIOREGIONS[name] = label


SUBNATIONAL_REGIONS = {
   "SUBN_Région_de_Bruxelles_Capit": "Région de Bruxelles-Capitale/Brussels Hoofdstedelijk Gewest (BE)",
   "SUBN_Prov__Antwerpen__BE_": "Prov. Antwerpen (BE)",
   "SUBN_Prov__Limburg__BE___BE_": "Prov. Limburg (BE) (BE)",
   "SUBN_Prov__Oost_Vlaanderen__BE": "Prov. Oost-Vlaanderen (BE)",
   "SUBN_Prov__Vlaams_Brabant__BE_": "Prov. Vlaams-Brabant (BE)",
   "SUBN_Prov__West_Vlaanderen__BE": "Prov. West-Vlaanderen (BE)",
   "SUBN_Prov__Brabant_Wallon__BE_": "Prov. Brabant Wallon (BE)",
   "SUBN_Prov__Hainaut__BE_": "Prov. Hainaut (BE)",
   "SUBN_Prov__Liège__BE_": "Prov. Liège (BE)",
   "SUBN_Prov__Luxembourg__BE___BE": "Prov. Luxembourg (BE) (BE)",
   "SUBN_Prov__Namur__BE_": "Prov. Namur (BE)",
   "SUBN_Extra_Regio_NUTS_2__BE_": "Extra-Regio NUTS 2 (BE)",
   "SUBN_Северозападен__Severozapa": "Северозападен (Severozapaden) (BG)",
   "SUBN_Северен_централен__Severe": "Северен централен (Severen tsentralen) (BG)",
   "SUBN_Североизточен__Severoizto": "Североизточен (Severoiztochen) (BG)",
   "SUBN_Югоизточен__Yugoiztochen_": "Югоизточен (Yugoiztochen) (BG)",
   "SUBN_Югозападен__Yugozapaden__": "Югозападен (Yugozapaden) (BG)",
   "SUBN_Южен_централен__Yuzhen_ts": "Южен централен (Yuzhen tsentralen) (BG)",
   "SUBN_Extra_Regio_NUTS_2__BG_": "Extra-Regio NUTS 2 (BG)",
   "SUBN_Praha__CZ_": "Praha (CZ)",
   "SUBN_Střední_Čechy__CZ_": "Střední Čechy (CZ)",
   "SUBN_Jihozápad__CZ_": "Jihozápad (CZ)",
   "SUBN_Severozápad__CZ_": "Severozápad (CZ)",
   "SUBN_Severovýchod__CZ_": "Severovýchod (CZ)",
   "SUBN_Jihovýchod__CZ_": "Jihovýchod (CZ)",
   "SUBN_Střední_Morava__CZ_": "Střední Morava (CZ)",
   "SUBN_Moravskoslezsko__CZ_": "Moravskoslezsko (CZ)",
   "SUBN_Extra_Regio_NUTS_2__CZ_": "Extra-Regio NUTS 2 (CZ)",
   "SUBN_Hovedstaden__DK_": "Hovedstaden (DK)",
   "SUBN_Sjælland__DK_": "Sjælland (DK)",
   "SUBN_Syddanmark__DK_": "Syddanmark (DK)",
   "SUBN_Midtjylland__DK_": "Midtjylland (DK)",
   "SUBN_Nordjylland__DK_": "Nordjylland (DK)",
   "SUBN_Extra_Regio_NUTS_2__DK_": "Extra-Regio NUTS 2 (DK)",
   "SUBN_Stuttgart__DE_": "Stuttgart (DE)",
   "SUBN_Karlsruhe__DE_": "Karlsruhe (DE)",
   "SUBN_Freiburg__DE_": "Freiburg (DE)",
   "SUBN_Tübingen__DE_": "Tübingen (DE)",
   "SUBN_Oberbayern__DE_": "Oberbayern (DE)",
   "SUBN_Niederbayern__DE_": "Niederbayern (DE)",
   "SUBN_Oberpfalz__DE_": "Oberpfalz (DE)",
   "SUBN_Oberfranken__DE_": "Oberfranken (DE)",
   "SUBN_Mittelfranken__DE_": "Mittelfranken (DE)",
   "SUBN_Unterfranken__DE_": "Unterfranken (DE)",
   "SUBN_Schwaben__DE_": "Schwaben (DE)",
   "SUBN_Berlin__DE_": "Berlin (DE)",
   "SUBN_Brandenburg__DE_": "Brandenburg (DE)",
   "SUBN_Bremen__DE_": "Bremen (DE)",
   "SUBN_Hamburg__DE_": "Hamburg (DE)",
   "SUBN_Darmstadt__DE_": "Darmstadt (DE)",
   "SUBN_Gießen__DE_": "Gießen (DE)",
   "SUBN_Kassel__DE_": "Kassel (DE)",
   "SUBN_Mecklenburg_Vorpommern__D": "Mecklenburg-Vorpommern (DE)",
   "SUBN_Braunschweig__DE_": "Braunschweig (DE)",
   "SUBN_Hannover__DE_": "Hannover (DE)",
   "SUBN_Lüneburg__DE_": "Lüneburg (DE)",
   "SUBN_Weser_Ems__DE_": "Weser-Ems (DE)",
   "SUBN_Düsseldorf__DE_": "Düsseldorf (DE)",
   "SUBN_Köln__DE_": "Köln (DE)",
   "SUBN_Münster__DE_": "Münster (DE)",
   "SUBN_Detmold__DE_": "Detmold (DE)",
   "SUBN_Arnsberg__DE_": "Arnsberg (DE)",
   "SUBN_Koblenz__DE_": "Koblenz (DE)",
   "SUBN_Trier__DE_": "Trier (DE)",
   "SUBN_Rheinhessen_Pfalz__DE_": "Rheinhessen-Pfalz (DE)",
   "SUBN_Saarland__DE_": "Saarland (DE)",
   "SUBN_Dresden__DE_": "Dresden (DE)",
   "SUBN_Chemnitz__DE_": "Chemnitz (DE)",
   "SUBN_Leipzig__DE_": "Leipzig (DE)",
   "SUBN_Sachsen_Anhalt__DE_": "Sachsen-Anhalt (DE)",
   "SUBN_Schleswig_Holstein__DE_": "Schleswig-Holstein (DE)",
   "SUBN_Thüringen__DE_": "Thüringen (DE)",
   "SUBN_Extra_Regio_NUTS_2__DE_": "Extra-Regio NUTS 2 (DE)",
   "SUBN_Eesti__EE_": "Eesti (EE)",
   "SUBN_Extra_Regio_NUTS_2__EE_": "Extra-Regio NUTS 2 (EE)",
   "SUBN_Border__Midland_and_Weste": "Border, Midland and Western (IE)",
   "SUBN_Southern_and_Eastern__IE_": "Southern and Eastern (IE)",
   "SUBN_Extra_Regio_NUTS_2__IE_": "Extra-Regio NUTS 2 (IE)",
   "SUBN_Aνατολική_Μακεδονία__Θράκ": "Aνατολική Μακεδονία, Θράκη (Anatoliki Makedonia, Thraki) (EL)",
   "SUBN_Κεντρική_Μακεδονία__Kentr": "Κεντρική Μακεδονία (Kentriki Makedonia) (EL)",
   "SUBN_Δυτική_Μακεδονία__Dytiki_": "Δυτική Μακεδονία (Dytiki Makedonia) (EL)",
   "SUBN_Θεσσαλία__Thessalia___EL_": "Θεσσαλία (Thessalia) (EL)",
   "SUBN_Ήπειρος__Ipeiros___EL_": "Ήπειρος (Ipeiros) (EL)",
   "SUBN_Ιόνια_Νησιά__Ionia_Nisia_": "Ιόνια Νησιά (Ionia Nisia) (EL)",
   "SUBN_Δυτική_Ελλάδα__Dytiki_Ell": "Δυτική Ελλάδα (Dytiki Ellada) (EL)",
   "SUBN_Στερεά_Ελλάδα__Sterea_Ell": "Στερεά Ελλάδα (Sterea Ellada) (EL)",
   "SUBN_Πελοπόννησος__Peloponniso": "Πελοπόννησος (Peloponnisos) (EL)",
   "SUBN_Aττική__Attiki___EL_": "Aττική (Attiki) (EL)",
   "SUBN_Βόρειο_Αιγαίο__Voreio_Aig": "Βόρειο Αιγαίο (Voreio Aigaio) (EL)",
   "SUBN_Νότιο_Αιγαίο__Notio_Aigai": "Νότιο Αιγαίο (Notio Aigaio) (EL)",
   "SUBN_Κρήτη__Kriti___EL_": "Κρήτη (Kriti) (EL)",
   "SUBN_Extra_Regio_NUTS_2__EL_": "Extra-Regio NUTS 2 (EL)",
   "SUBN_Galicia__ES_": "Galicia (ES)",
   "SUBN_Principado_de_Asturias__E": "Principado de Asturias (ES)",
   "SUBN_Cantabria__ES_": "Cantabria (ES)",
   "SUBN_País_Vasco__ES_": "País Vasco (ES)",
   "SUBN_Comunidad_Foral_de_Navarr": "Comunidad Foral de Navarra (ES)",
   "SUBN_La_Rioja__ES_": "La Rioja (ES)",
   "SUBN_Aragón__ES_": "Aragón (ES)",
   "SUBN_Comunidad_de_Madrid__ES_": "Comunidad de Madrid (ES)",
   "SUBN_Castilla_y_León__ES_": "Castilla y León (ES)",
   "SUBN_Castilla_La_Mancha__ES_": "Castilla-La Mancha (ES)",
   "SUBN_Extremadura__ES_": "Extremadura (ES)",
   "SUBN_Cataluña__ES_": "Cataluña (ES)",
   "SUBN_Comunidad_Valenciana__ES_": "Comunidad Valenciana (ES)",
   "SUBN_Illes_Balears__ES_": "Illes Balears (ES)",
   "SUBN_Andalucía__ES_": "Andalucía (ES)",
   "SUBN_Región_de_Murcia__ES_": "Región de Murcia (ES)",
   "SUBN_Ciudad_Autónoma_de_Ceuta_": "Ciudad Autónoma de Ceuta (ES)",
   "SUBN_Ciudad_Autónoma_de_Melill": "Ciudad Autónoma de Melilla (ES)",
   "SUBN_Canarias__ES_": "Canarias (ES)",
   "SUBN_Extra_Regio_NUTS_2__ES_": "Extra-Regio NUTS 2 (ES)",
   "SUBN_Île_de_France__FR_": "Île de France (FR)",
   "SUBN_Champagne_Ardenne__FR_": "Champagne-Ardenne (FR)",
   "SUBN_Picardie__FR_": "Picardie (FR)",
   "SUBN_Haute_Normandie__FR_": "Haute-Normandie (FR)",
   "SUBN_Centre__FR_": "Centre (FR)",
   "SUBN_Basse_Normandie__FR_": "Basse-Normandie (FR)",
   "SUBN_Bourgogne__FR_": "Bourgogne (FR)",
   "SUBN_Nord___Pas_de_Calais__FR_": "Nord - Pas-de-Calais (FR)",
   "SUBN_Lorraine__FR_": "Lorraine (FR)",
   "SUBN_Alsace__FR_": "Alsace (FR)",
   "SUBN_Franche_Comté__FR_": "Franche-Comté (FR)",
   "SUBN_Pays_de_la_Loire__FR_": "Pays de la Loire (FR)",
   "SUBN_Bretagne__FR_": "Bretagne (FR)",
   "SUBN_Poitou_Charentes__FR_": "Poitou-Charentes (FR)",
   "SUBN_Aquitaine__FR_": "Aquitaine (FR)",
   "SUBN_Midi_Pyrénées__FR_": "Midi-Pyrénées (FR)",
   "SUBN_Limousin__FR_": "Limousin (FR)",
   "SUBN_Rhône_Alpes__FR_": "Rhône-Alpes (FR)",
   "SUBN_Auvergne__FR_": "Auvergne (FR)",
   "SUBN_Languedoc_Roussillon__FR_": "Languedoc-Roussillon (FR)",
   "SUBN_Provence_Alpes_Côte_d_Azu": "Provence-Alpes-Côte d'Azur (FR)",
   "SUBN_Corse__FR_": "Corse (FR)",
   "SUBN_Guadeloupe__FR_": "Guadeloupe (FR)",
   "SUBN_Martinique__FR_": "Martinique (FR)",
   "SUBN_Guyane__FR_": "Guyane (FR)",
   "SUBN_Réunion__FR_": "Réunion (FR)",
   "SUBN_Extra_Regio_NUTS_2__FR_": "Extra-Regio NUTS 2 (FR)",
   "SUBN_Extra_Regio_NUTS_2__HR_": "Extra-Regio NUTS 2 (HR)",
   "SUBN_Piemonte__IT_": "Piemonte (IT)",
   "SUBN_Valle_d_Aosta_Vallée_d_Ao": "Valle d'Aosta/Vallée d'Aoste (IT)",
   "SUBN_Liguria__IT_": "Liguria (IT)",
   "SUBN_Lombardia__IT_": "Lombardia (IT)",
   "SUBN_Abruzzo__IT_": "Abruzzo (IT)",
   "SUBN_Molise__IT_": "Molise (IT)",
   "SUBN_Campania__IT_": "Campania (IT)",
   "SUBN_Puglia__IT_": "Puglia (IT)",
   "SUBN_Basilicata__IT_": "Basilicata (IT)",
   "SUBN_Calabria__IT_": "Calabria (IT)",
   "SUBN_Sicilia__IT_": "Sicilia (IT)",
   "SUBN_Sardegna__IT_": "Sardegna (IT)",
   "SUBN_Provincia_Autonoma_di_Bol": "Provincia Autonoma di Bolzano/Bozen (IT)",
   "SUBN_Provincia_Autonoma_di_Tre": "Provincia Autonoma di Trento (IT)",
   "SUBN_Veneto__IT_": "Veneto (IT)",
   "SUBN_Friuli_Venezia_Giulia__IT": "Friuli-Venezia Giulia (IT)",
   "SUBN_Emilia_Romagna__IT_": "Emilia-Romagna (IT)",
   "SUBN_Toscana__IT_": "Toscana (IT)",
   "SUBN_Umbria__IT_": "Umbria (IT)",
   "SUBN_Marche__IT_": "Marche (IT)",
   "SUBN_Lazio__IT_": "Lazio (IT)",
   "SUBN_Extra_Regio_NUTS_2__IT_": "Extra-Regio NUTS 2 (IT)",
   "SUBN_Κύπρος__Kýpros___CY_": "Κύπρος (Kýpros) (CY)",
   "SUBN_Extra_Regio_NUTS_2__CY_": "Extra-Regio NUTS 2 (CY)",
   "SUBN_Latvija__LV_": "Latvija (LV)",
   "SUBN_Extra_Regio_NUTS_2__LV_": "Extra-Regio NUTS 2 (LV)",
   "SUBN_Lietuva__LT_": "Lietuva (LT)",
   "SUBN_Extra_Regio_NUTS_2__LT_": "Extra-Regio NUTS 2 (LT)",
   "SUBN_Luxembourg__LU_": "Luxembourg (LU)",
   "SUBN_Extra_Regio_NUTS_2__LU_": "Extra-Regio NUTS 2 (LU)",
   "SUBN_Közép_Magyarország__HU_": "Közép-Magyarország (HU)",
   "SUBN_Közép_Dunántúl__HU_": "Közép-Dunántúl (HU)",
   "SUBN_Nyugat_Dunántúl__HU_": "Nyugat-Dunántúl (HU)",
   "SUBN_Dél_Dunántúl__HU_": "Dél-Dunántúl (HU)",
   "SUBN_Észak_Magyarország__HU_": "Észak-Magyarország (HU)",
   "SUBN_Észak_Alföld__HU_": "Észak-Alföld (HU)",
   "SUBN_Dél_Alföld__HU_": "Dél-Alföld (HU)",
   "SUBN_Extra_Regio_NUTS_2__HU_": "Extra-Regio NUTS 2 (HU)",
   "SUBN_Malta__MT_": "Malta (MT)",
   "SUBN_Extra_Regio_NUTS_2__MT_": "Extra-Regio NUTS 2 (MT)",
   "SUBN_Groningen__NL_": "Groningen (NL)",
   "SUBN_Friesland__NL___NL_": "Friesland (NL) (NL)",
   "SUBN_Drenthe__NL_": "Drenthe (NL)",
   "SUBN_Overijssel__NL_": "Overijssel (NL)",
   "SUBN_Gelderland__NL_": "Gelderland (NL)",
   "SUBN_Flevoland__NL_": "Flevoland (NL)",
   "SUBN_Utrecht__NL_": "Utrecht (NL)",
   "SUBN_Noord_Holland__NL_": "Noord-Holland (NL)",
   "SUBN_Zuid_Holland__NL_": "Zuid-Holland (NL)",
   "SUBN_Zeeland__NL_": "Zeeland (NL)",
   "SUBN_Noord_Brabant__NL_": "Noord-Brabant (NL)",
   "SUBN_Limburg__NL___NL_": "Limburg (NL) (NL)",
   "SUBN_Extra_Regio_NUTS_2__NL_": "Extra-Regio NUTS 2 (NL)",
   "SUBN_Burgenland__AT___AT_": "Burgenland (AT) (AT)",
   "SUBN_Niederösterreich__AT_": "Niederösterreich (AT)",
   "SUBN_Wien__AT_": "Wien (AT)",
   "SUBN_Kärnten__AT_": "Kärnten (AT)",
   "SUBN_Steiermark__AT_": "Steiermark (AT)",
   "SUBN_Oberösterreich__AT_": "Oberösterreich (AT)",
   "SUBN_Salzburg__AT_": "Salzburg (AT)",
   "SUBN_Tirol__AT_": "Tirol (AT)",
   "SUBN_Vorarlberg__AT_": "Vorarlberg (AT)",
   "SUBN_Extra_Regio_NUTS_2__AT_": "Extra-Regio NUTS 2 (AT)",
   "SUBN_Łódzkie__PL_": "Łódzkie (PL)",
   "SUBN_Mazowieckie__PL_": "Mazowieckie (PL)",
   "SUBN_Małopolskie__PL_": "Małopolskie (PL)",
   "SUBN_Śląskie__PL_": "Śląskie (PL)",
   "SUBN_Lubelskie__PL_": "Lubelskie (PL)",
   "SUBN_Podkarpackie__PL_": "Podkarpackie (PL)",
   "SUBN_Świętokrzyskie__PL_": "Świętokrzyskie (PL)",
   "SUBN_Podlaskie__PL_": "Podlaskie (PL)",
   "SUBN_Wielkopolskie__PL_": "Wielkopolskie (PL)",
   "SUBN_Zachodniopomorskie__PL_": "Zachodniopomorskie (PL)",
   "SUBN_Lubuskie__PL_": "Lubuskie (PL)",
   "SUBN_Dolnośląskie__PL_": "Dolnośląskie (PL)",
   "SUBN_Opolskie__PL_": "Opolskie (PL)",
   "SUBN_Kujawsko_Pomorskie__PL_": "Kujawsko-Pomorskie (PL)",
   "SUBN_Warmińsko_Mazurskie__PL_": "Warmińsko-Mazurskie (PL)",
   "SUBN_Pomorskie__PL_": "Pomorskie (PL)",
   "SUBN_Extra_Regio_NUTS_2__PL_": "Extra-Regio NUTS 2 (PL)",
   "SUBN_Norte__PT_": "Norte (PT)",
   "SUBN_Algarve__PT_": "Algarve (PT)",
   "SUBN_Centro__PT___PT_": "Centro (PT) (PT)",
   "SUBN_Lisboa__PT_": "Lisboa (PT)",
   "SUBN_Alentejo__PT_": "Alentejo (PT)",
   "SUBN_Região_Autónoma_dos_Açore": "Região Autónoma dos Açores (PT)",
   "SUBN_Região_Autónoma_da_Madeir": "Região Autónoma da Madeira (PT)",
   "SUBN_Extra_Regio_NUTS_2__PT_": "Extra-Regio NUTS 2 (PT)",
   "SUBN_Nord_Vest__RO_": "Nord-Vest (RO)",
   "SUBN_Centru__RO_": "Centru (RO)",
   "SUBN_Nord_Est__RO_": "Nord-Est (RO)",
   "SUBN_Sud_Est__RO_": "Sud-Est (RO)",
   "SUBN_Sud___Muntenia__RO_": "Sud - Muntenia (RO)",
   "SUBN_Bucureşti___Ilfov__RO_": "Bucureşti - Ilfov (RO)",
   "SUBN_Sud_Vest_Oltenia__RO_": "Sud-Vest Oltenia (RO)",
   "SUBN_Vest__RO_": "Vest (RO)",
   "SUBN_Extra_Regio_NUTS_2__RO_": "Extra-Regio NUTS 2 (RO)",
   "SUBN_Vzhodna_Slovenija__SI_": "Vzhodna Slovenija (SI)",
   "SUBN_Zahodna_Slovenija__SI_": "Zahodna Slovenija (SI)",
   "SUBN_Extra_Regio_NUTS_2__SI_": "Extra-Regio NUTS 2 (SI)",
   "SUBN_Bratislavský_kraj__SK_": "Bratislavský kraj (SK)",
   "SUBN_Západné_Slovensko__SK_": "Západné Slovensko (SK)",
   "SUBN_Stredné_Slovensko__SK_": "Stredné Slovensko (SK)",
   "SUBN_Východné_Slovensko__SK_": "Východné Slovensko (SK)",
   "SUBN_Extra_Regio_NUTS_2__SK_": "Extra-Regio NUTS 2 (SK)",
   "SUBN_Länsi_Suomi__FI_": "Länsi-Suomi (FI)",
   "SUBN_Helsinki_Uusimaa__FI_": "Helsinki-Uusimaa (FI)",
   "SUBN_Etelä_Suomi__FI_": "Etelä-Suomi (FI)",
   "SUBN_Pohjois__ja_Itä_Suomi__FI": "Pohjois- ja Itä-Suomi (FI)",
   "SUBN_Åland__FI_": "Åland (FI)",
   "SUBN_Extra_Regio_NUTS_2__FI_": "Extra-Regio NUTS 2 (FI)",
   "SUBN_Stockholm__SE_": "Stockholm (SE)",
   "SUBN_Östra_Mellansverige__SE_": "Östra Mellansverige (SE)",
   "SUBN_Småland_med_öarna__SE_": "Småland med öarna (SE)",
   "SUBN_Sydsverige__SE_": "Sydsverige (SE)",
   "SUBN_Västsverige__SE_": "Västsverige (SE)",
   "SUBN_Norra_Mellansverige__SE_": "Norra Mellansverige (SE)",
   "SUBN_Mellersta_Norrland__SE_": "Mellersta Norrland (SE)",
   "SUBN_Övre_Norrland__SE_": "Övre Norrland (SE)",
   "SUBN_Extra_Regio_NUTS_2__SE_": "Extra-Regio NUTS 2 (SE)",
   "SUBN_Tees_Valley_and_Durham__U": "Tees Valley and Durham (UK)",
   "SUBN_Northumberland_and_Tyne_a": "Northumberland and Tyne and Wear (UK)",
   "SUBN_Cumbria__UK_": "Cumbria (UK)",
   "SUBN_Greater_Manchester__UK_": "Greater Manchester (UK)",
   "SUBN_Lancashire__UK_": "Lancashire (UK)",
   "SUBN_Cheshire__UK_": "Cheshire (UK)",
   "SUBN_Merseyside__UK_": "Merseyside (UK)",
   "SUBN_East_Yorkshire_and_Northe": "East Yorkshire and Northern Lincolnshire (UK)",
   "SUBN_North_Yorkshire__UK_": "North Yorkshire (UK)",
   "SUBN_South_Yorkshire__UK_": "South Yorkshire (UK)",
   "SUBN_West_Yorkshire__UK_": "West Yorkshire (UK)",
   "SUBN_Derbyshire_and_Nottingham": "Derbyshire and Nottinghamshire (UK)",
   "SUBN_Leicestershire__Rutland_a": "Leicestershire, Rutland and Northamptonshire (UK)",
   "SUBN_Lincolnshire__UK_": "Lincolnshire (UK)",
   "SUBN_Herefordshire__Worcesters": "Herefordshire, Worcestershire and Warwickshire (UK)",
   "SUBN_Shropshire_and_Staffordsh": "Shropshire and Staffordshire (UK)",
   "SUBN_West_Midlands__UK_": "West Midlands (UK)",
   "SUBN_East_Anglia__UK_": "East Anglia (UK)",
   "SUBN_Bedfordshire_and_Hertford": "Bedfordshire and Hertfordshire (UK)",
   "SUBN_Essex__UK_": "Essex (UK)",
   "SUBN_Inner_London__UK_": "Inner London (UK)",
   "SUBN_Outer_London__UK_": "Outer London (UK)",
   "SUBN_Berkshire__Buckinghamshir": "Berkshire, Buckinghamshire and Oxfordshire (UK)",
   "SUBN_Surrey__East_and_West_Sus": "Surrey, East and West Sussex (UK)",
   "SUBN_Hampshire_and_Isle_of_Wig": "Hampshire and Isle of Wight (UK)",
   "SUBN_Kent__UK_": "Kent (UK)",
   "SUBN_Gloucestershire__Wiltshir": "Gloucestershire, Wiltshire and Bristol/Bath area (UK)",
   "SUBN_Dorset_and_Somerset__UK_": "Dorset and Somerset (UK)",
   "SUBN_Cornwall_and_Isles_of_Sci": "Cornwall and Isles of Scilly (UK)",
   "SUBN_Devon__UK_": "Devon (UK)",
   "SUBN_West_Wales_and_The_Valley": "West Wales and The Valleys (UK)",
   "SUBN_East_Wales__UK_": "East Wales (UK)",
   "SUBN_Eastern_Scotland__UK_": "Eastern Scotland (UK)",
   "SUBN_South_Western_Scotland__U": "South Western Scotland (UK)",
   "SUBN_North_Eastern_Scotland__U": "North Eastern Scotland (UK)",
   "SUBN_Highlands_and_Islands__UK": "Highlands and Islands (UK)",
   "SUBN_Northern_Ireland__UK_": "Northern Ireland (UK)",
   "SUBN_Extra_Regio_NUTS_2__UK_": "Extra-Regio NUTS 2 (UK)",
   }
