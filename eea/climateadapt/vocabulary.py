from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm


def generic_vocabulary(_terms):

    if _terms and isinstance(_terms[0], basestring):
        _terms = [(x, x) for x in _terms]

    def factory(context):
        return SimpleVocabulary([
            SimpleTerm(n, n, l) for n, l in _terms
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

def aceitem_datatypes_vocabulary(context):
    """ AceItem data types """

    terms = []
    for line in filter(None, _datatypes.split('\n')):
        first, label = line.split('=')
        name = first.split('acesearch-datainfotype-lbl-')[1]
        terms.append((name, label))

    terms.sort(cmp=lambda x,y: cmp(x[1], y[1]))

    return SimpleVocabulary([
        SimpleTerm(n, n, l) for n, l in terms
    ])

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

