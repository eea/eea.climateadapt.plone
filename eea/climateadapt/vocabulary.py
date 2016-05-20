from Products.CMFCore.utils import getToolByName
from collections import namedtuple
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import pycountry


def generic_vocabulary(_terms):
    """ Returns a zope vocabulary from a dict or a list
    """

    if _terms and isinstance(_terms, dict):
        _terms = sorted(dict.items())
    elif _terms and isinstance(_terms[0], basestring):
        _terms = [(x, x) for x in _terms]

    def factory(context):
        return SimpleVocabulary([
            SimpleTerm(n, n, l) for n, l in _terms
        ])

    return factory


def catalog_based_vocabulary(index):
    """ Creates a vocabulary from searching on an index
    """

    def factory(context):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        terms = catalog.uniqueValuesFor(index)
        terms = sorted(terms)

        return SimpleVocabulary([
            SimpleTerm(x, x, x) for x in terms
        ])

        pass

    return factory


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
    ("ORGANISATION", "Organisations"),
    ("MEASURE", "Adaptation options"),
    ("ACTION", "Case studies"),
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
    ("INFRASTRUCTURE", "Infrastructure"),
    ("URBAN", "Urban"),
    ("MARINE", "Marine and Fisheries"),
#   ("TOURISM", "Tourism"),
#   ("ENERGY", "Energy"),
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
    ('OTHER_POL_OBJ', 'Case mainly developed and implemented because of other policy objectives, but with significant'),
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
                      'MK', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'RU', 'SE',
                      'SI', 'SK', 'SM', 'TR', 'UA']
ace_countries = [(x.alpha2, x.name) for x in pycountry.countries
                 if x.alpha2 in european_countries]
ace_countries.append(('FYROM', 'F. Y. R. O. Macedonia'))
ace_countries_dict = dict(ace_countries)

ace_countries_vocabulary = generic_vocabulary(ace_countries)
alsoProvides(ace_countries_vocabulary, IVocabularyFactory)

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

special_tags_vocabulary = catalog_based_vocabulary('special_tags')
alsoProvides(special_tags_vocabulary, IVocabularyFactory)
