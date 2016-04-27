from Products.CMFCore.utils import getToolByName
from collections import namedtuple
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import pycountry


def generic_vocabulary(_terms):
    if _terms and isinstance(_terms, dict):
        _terms = dict.items()
    elif _terms and isinstance(_terms[0], basestring):
        _terms = [(x, x) for x in _terms]

    def factory(context):
        return SimpleVocabulary([
            SimpleTerm(n, n, l) for n, l in _terms
        ])

    return factory


def vocab_from_labels(text):
    def factory(context):
        """ AceItem data types """

        terms = []
        for line in filter(None, text.split('\n')):
            first, label = line.split('=')
            name = first.split('-lbl-')[1]
            terms.append((name, label))

        terms.sort(cmp=lambda x, y: cmp(x[1], y[1]))

        return SimpleVocabulary([
            SimpleTerm(n, n, l) for n, l in terms
        ])

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
    ("TOURISM", "Tourism"),
    ("ENERGY", "Energy"),
    ("OTHER", "Other"),
    ("WATERMANAGEMENT", "Water management")
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
    ("FORESTFIRES", "Forest Fires"),
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


_covenant = [
    ("", "Select"),
    ("YES", "Yes"),
    ("NO", "No"),
]
covenant_vocabulary = generic_vocabulary(_covenant)
alsoProvides(covenant_vocabulary, IVocabularyFactory)


_status_of_adapt_signature = [
    ("", "Select"),
    ("ALREADYSIGNED", "Already Signed"),
    ("INPROCESSSIGNING", "In the process of signing"),
]
status_of_adapt_signature_vocabulary = generic_vocabulary(_status_of_adapt_signature)
alsoProvides(status_of_adapt_signature_vocabulary, IVocabularyFactory)


# TODO: merge with _sectors vocabulary
_key_vulnerable_adapt_sector = [
    ("AGRI_AND_FOREST", "Agriculture and Forest"),
    ("COASTAL_AREAS", "Coastal areas"),
    ("DISASTER_RISK", "Disaster Risk Reduction"),
    ("FINANCIAL", "Financial"),
    ("HEALTH", "Health"),
    ("INFRASTRUCTURE", "Infrastructure"),
    ("MARINE_AND_FISH", "Marine and Fisheries"),
    ("TOURISM", "Tourism"),
    ("ENERGY", "Energy"),
    ("OTHER", "Other"),
    ("BIODIVERSITY", "Biodiversity"),
    ("WATER_MANAGEMENT", "Water Management"),
    ("URBAN", "Urban"),
]
key_vulnerable_adapt_sector_vocabulary = generic_vocabulary(_key_vulnerable_adapt_sector)
alsoProvides(key_vulnerable_adapt_sector_vocabulary, IVocabularyFactory)


_stage_implementation_cycle = [
    ("PREPARING_GROUND", "Preparing the ground"),
    ("ASSESSING_RISKS_VULNER", "Assessing risks and vulnerabilities"),
    ("IDENTIF_ADAPT_OPT", "Identifying adaptation options"),
    ("ASSESSING_ADAPT_OPT", "Assessing adaptation options"),
    ("IMPLEMENTATION", "Implementation"),
    ("MONIT_AND_EVAL", "Monitoring and evaluation"),
]
stage_implementation_cycle_vocabulary = generic_vocabulary(_stage_implementation_cycle)
alsoProvides(stage_implementation_cycle_vocabulary, IVocabularyFactory)


_already_devel_adapt_strategy = [
    ("", "Select"),
    ("YES_HAVE_ADAPT_STRAT", "Yes, we have an adaptation strategy"),
    ("NO_HAVE_ADAPT_STRAT", "No, we do not have an adaptation strategy but are currently developing one"),
    ("MAYORS_ADAPT_FIRST_EX", "No, Mayors Adapt is the first example of my city considering adaptation and we will develop an adaptation strategy"),
    ("INTEG_ADAPT_EXIST_REL", "We (will) integrate adaptation into existing relevant plans"),
]
already_devel_adapt_strategy_vocabulary = generic_vocabulary(_already_devel_adapt_strategy)
alsoProvides(already_devel_adapt_strategy_vocabulary, IVocabularyFactory)


# TODO: isn't this the same vocabulary as _elements
_elements_mentioned_your_cp = [
    ("EU_POLICY", "Sector Policies"),
    ("MEASUREACTION", "Adaptation Measures and Actions"),
    ("OBSERVATIONS", "Observations and Scenarios"),
    ("PLANSTRATEGY", "Adaptation Plans and Strategies"),
    ("VULNERABILITY", "Vulnerability Assessment"),
]

elements_mentioned_your_cp_vocabulary = generic_vocabulary(_elements_mentioned_your_cp)
alsoProvides(elements_mentioned_your_cp_vocabulary, IVocabularyFactory)


def catalog_based_vocabulary(index):

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

search_types_vocabulary = catalog_based_vocabulary('search_type')
alsoProvides(search_types_vocabulary, IVocabularyFactory)

element_types_vocabulary = catalog_based_vocabulary('elements')
alsoProvides(element_types_vocabulary, IVocabularyFactory)

special_tags_vocabulary = catalog_based_vocabulary('special_tags')
alsoProvides(special_tags_vocabulary, IVocabularyFactory)
