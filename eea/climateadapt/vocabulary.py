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


def catalog_based_vocabulary(index):
    """ Creates a vocabulary from searching on an index
    """

    def factory(context):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        terms = catalog.uniqueValuesFor(index)
        terms = sorted(terms)

        return SimpleVocabulary([
            SimpleTerm(x, x.encode('utf-8'), x) for x in terms
        ])

    return factory


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
    ("AGRICULTURE", "Agriculture and Forest"),
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


european_countries = ['AD', 'AL', 'AM', 'AT', 'AZ', 'BA', 'BE', 'BG', 'BY',
                      'CH', 'RS', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
                      'FO', 'FR', 'GB', 'GE', 'GR', 'HR', 'HU', 'IE', 'IL',
                      'IS', 'IT', 'KZ', 'LI', 'LT', 'LU', 'LV', 'MC', 'MD',
                      'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE', 'SI',
                      'SK', 'SM', 'TR', 'UA']
ace_countries = [(x.alpha2, x.name) for x in pycountry.countries
                 if x.alpha2 in european_countries]
ace_countries.append(('FYROM', 'F. Y. R. O. Macedonia'))
ace_countries.append(('MK', 'Republic of Macedonia'))
ace_countries_dict = dict(ace_countries)

ace_countries_vocabulary = generic_vocabulary(ace_countries)
alsoProvides(ace_countries_vocabulary, IVocabularyFactory)


eu_countries_selection = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR',
                          'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'LV', 'LI', 'LT', 'LU',
                          'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE',
                          'CH', 'TR', 'GB']
ace_countries_selection = [(x.alpha2, x.name) for x in pycountry.countries
                          if x.alpha2 in eu_countries_selection]

faceted_countries = ['AL', 'AT', 'BE', 'BG', 'BA', 'HR', 'CY', 'CZ', 'DK',
                     'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT',
                     'KZ', 'LV', 'LI', 'LT', 'LU', 'MT', 'ME', 'NL', 'NO',
                     'PL', 'PT', 'RO', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH',
                     'TR', 'GB']
faceted_countries = [(x.alpha2, x.name) for x in pycountry.countries
                     if x.alpha2 in faceted_countries]
faceted_countries.append(('FYROM', 'F. Y. R. O. Macedonia'))
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

# keywords_vocabulary = catalog_based_vocabulary('keywords')
# alsoProvides(keywords_vocabulary, IVocabularyFactory)

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
