""" Utilities for faceted search
"""

from Products.Five.browser import BrowserView
from collections import defaultdict
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


FACETED_SEARCH_TYPES = [
    ("CITYPROFILE", "Mayors Adapt city profiles"),
    ("COVER", "Content in Climate-ADAPT"),
    ("DOCUMENT", "Publication & Report"),
    ("INFORMATIONSOURCE", "Information Portal"),
    ("GUIDANCE","Guidance"),
    ("TOOL", "Tools"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("RESEARCHPROJECT","Research and knowledge Projects"),
    ("MEASURE","Adaptation Option"),
    ("ACTION", "Case Studies"),
    ("ORGANISATION", "Organisations"),
]


class ListingView(BrowserView):
    """ Faceted listing view for ClimateAdapt
    """

    @property
    def sections(self):
        return [x[0] for x in FACETED_SEARCH_TYPES]

    @property
    def labels(self):
        return dict(FACETED_SEARCH_TYPES)

    def results(self, batch):
        results = defaultdict(lambda:[])
        for brain in batch:
            if brain.search_type:
                if brain.search_type in self.labels:
                    results[brain.search_type].append(brain)

        print results
        return results
