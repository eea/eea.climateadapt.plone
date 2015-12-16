""" Utilities for faceted search
"""

from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


SEARCH_TYPES = [
    ("DOCUMENT", "Publication & Report"),
    ("INFORMATIONSOURCE", "Information Portal"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("GUIDANCE","Guidance"),
    ("TOOL", "Tools"),
    ("RESEARCHPROJECT","Research and knowledge projects"),
    ("MEASURE","Adaptation options"),
    ("ACTION", "Case studies"),
    ("ORGANISATION", "Organisations"),

    # TODO: add "Mayors Adapt City profiles"
    # TODO: add "Content in Climate-ADAPT"
]


def search_types_vocabulary(context):


    return SimpleVocabulary([
        SimpleTerm(x[0], x[0], x[1]) for x in SEARCH_TYPES
    ])

alsoProvides(search_types_vocabulary, IVocabularyFactory)
