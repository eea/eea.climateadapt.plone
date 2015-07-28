from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


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

        terms.sort(cmp=lambda x,y: cmp(x[1], y[1]))

        return SimpleVocabulary([
            SimpleTerm(n, n, l) for n, l in terms
        ])

    return factory


# changes title and buttons (what to add) in view for AceItem
# extracted from JAVA code:
_datatypes = """
acesearch-datainfotype-lbl-DOCUMENT=Publications and reports
acesearch-datainfotype-lbl-INFORMATIONSOURCE=Information portals
acesearch-datainfotype-lbl-MAPGRAPHDATASET=Maps, graphs and datasets
acesearch-datainfotype-lbl-INDICATOR=Indicators
acesearch-datainfotype-lbl-GUIDANCE=Guidance
acesearch-datainfotype-lbl-TOOL=Tools
acesearch-datainfotype-lbl-RESEARCHPROJECT=Research and knowledge projects
acesearch-datainfotype-lbl-ORGANISATION=Organisations
acesearch-datainfotype-lbl-MEASURE=Adaptation options
acesearch-datainfotype-lbl-ACTION=Case studies
"""
aceitem_datatypes_vocabulary = vocab_from_labels(_datatypes)
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


_sectors = """
acesearch-sectors-lbl-AGRICULTURE=Agriculture and Forest
acesearch-sectors-lbl-BIODIVERSITY=Biodiversity
acesearch-sectors-lbl-COASTAL=Coastal areas
acesearch-sectors-lbl-DISASTERRISKREDUCTION=Disaster Risk Reduction
acesearch-sectors-lbl-FINANCIAL=Financial
acesearch-sectors-lbl-HEALTH=Health
acesearch-sectors-lbl-INFRASTRUCTURE=Infrastructure
acesearch-sectors-lbl-URBAN=Urban
acesearch-sectors-lbl-MARINE=Marine and Fisheries
acesearch-sectors-lbl-WATERMANAGEMENT=Water management
"""
aceitem_sectors_vocabulary = vocab_from_labels(_sectors)
alsoProvides(aceitem_sectors_vocabulary, IVocabularyFactory)


_elements = """
acesearch-elements-lbl-OBSERVATIONS=Observations and Scenarios
acesearch-elements-lbl-VULNERABILITY=Vulnerability Assessment
acesearch-elements-lbl-ACTION=Adaptation Actions
acesearch-elements-lbl-PLANSTRATEGY=Adaptation Plans and Strategies
acesearch-elements-lbl-EU_POLICY=Sector Policies
acesearch-elements-lbl-MEASUREACTION=Adaptation Measures and Actions
"""
aceitem_elements_vocabulary = vocab_from_labels(_elements)
alsoProvides(aceitem_elements_vocabulary, IVocabularyFactory)


_climateimpacts = """
aceitem-climateimpacts-lbl-EXTREMETEMP=Temperatures
aceitem-climateimpacts-lbl-WATERSCARCE=Water Scarcity
aceitem-climateimpacts-lbl-FLOODING=Flooding
aceitem-climateimpacts-lbl-SEALEVELRISE=Sea Level Rise
aceitem-climateimpacts-lbl-DROUGHT=Droughts
aceitem-climateimpacts-lbl-STORM=Storms
aceitem-climateimpacts-lbl-ICEANDSNOW=Ice and Snow
"""
aceitem_climateimpacts_vocabulary = vocab_from_labels(_climateimpacts)
alsoProvides(aceitem_climateimpacts_vocabulary, IVocabularyFactory)


_featured = [('CASEHOME', 'Feature this on the homepage'),
             ('CASESEARCH', 'Feature this on study search results page')]
aceitem_featured_vocabulary = generic_vocabulary(_featured)
alsoProvides(aceitem_featured_vocabulary, IVocabularyFactory)

_implementationtypes = (("grey", "Technical ('grey')"),
                        ("green", "Ecological ('green')"),
                        ("soft", "Behavioural / policy ('soft')")
                        )
acemeasure_implementationtype_vocabulary = generic_vocabulary(_implementationtypes)
alsoProvides(acemeasure_implementationtype_vocabulary, IVocabularyFactory)

from eea.vocab.countries import getCountries
ace_countries_vocabulary = generic_vocabulary(getCountries())

_measure_types = (("A", "Case study"), ("M", "Adaptation option"))
acemeasure_types = generic_vocabulary(_measure_types)
