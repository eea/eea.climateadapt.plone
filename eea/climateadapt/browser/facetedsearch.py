""" Utilities for faceted search
"""

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collections import defaultdict
from eea.facetednavigation.browser.app.view import FacetedContainerView
from plone import api
from plone.api import portal
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from eea.cache import cache


# TODO: should use the FACETED_SECTIONS LIST
SEARCH_TYPES = [
    ("CONTENT", "Content in Climate-ADAPT"),
    ("DOCUMENT", "Publication and Reports"),
    ("INFORMATIONSOURCE", "Information Portals"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("INDICATOR", "Indicators"),
    ("GUIDANCE", "Guidance"),
    ("TOOL", "Tools"),
    ("RESEARCHPROJECT", "Research and knowledge projects"),
    ("MEASURE", "Adaptation options"),
    ("ACTION", "Case studies"),
    ("MAYORSADAPT", "Mayors Adapt city profiles"),
    ("ORGANISATION", "Organisations"),
]

FACETED_SEARCH_TYPES = [
    ("MEASURE", "Adaptation options"),
    ("ACTION", "Case studies"),
    ("GUIDANCE", "Guidance"),
    ("INDICATOR", "Indicators"),
    ("INFORMATIONSOURCE", "Information Portals"),
    ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
    ("MAYORSADAPT", "Mayors Adapt city profiles"),
    ("ORGANISATION", "Organisations"),
    ("DOCUMENT", "Publication and Reports"),
    ("RESEARCHPROJECT", "Research and knowledge projects"),
    ("TOOL", "Tools"),
]


def faceted_search_types_vocabulary(context):

    return SimpleVocabulary([
        SimpleTerm(x[0], x[0], x[1]) for x in FACETED_SEARCH_TYPES
    ])

alsoProvides(faceted_search_types_vocabulary, IVocabularyFactory)


# FACETED_SECTIONS = [
#     ("CITYPROFILE", "Mayors Adapt city profiles"),
#     ("CONTENT", "Content in Climate-ADAPT"),
#     ("DOCUMENT", "Publication & Report"),
#     ("INFORMATIONSOURCE", "Information Portal"),
#     ("GUIDANCE","Guidance"),
#     ("TOOL", "Tools"),
#     ("MAPGRAPHDATASET", "Maps, graphs and datasets"),
#     ("INDICATOR", "Indicators"),
#     ("RESEARCHPROJECT","Research and knowledge Projects"),
#     ("MEASURE","Adaptation Option"),
#     ("ACTION", "Case Studies"),
#     ("ORGANISATION", "Organisations"),
# ]
#

class ListingView(BrowserView):
    """ Faceted listing view for ClimateAdapt
    """

    @property
    def sections(self):
        return [x[0] for x in SEARCH_TYPES]

    @property
    def labels(self):
        return dict(SEARCH_TYPES)

    def results(self, batch):
        results = defaultdict(lambda: [])
        for brain in batch:
            if brain.search_type:
                if brain.search_type in self.labels:
                    results[brain.search_type].append(brain)

        return results

    # def key(method, self, name, brains):
    #     print "caching ", name
    #     return method.__name__

    # @cache(key, lifetime=40)
    def render(self, name, brains):
        print "rendering ", name

        view = queryMultiAdapter((self.context, self.request),
                                 name='faceted_listing_' + name)
        if view is None:
            view = getMultiAdapter((self.context, self.request),
                                   name='faceted_listing_GENERIC')

        view.brains = brains
        return view()


class FacetedSearchTextPortlet(BrowserView):
    template = ViewPageTemplateFile("pt/search/faceted-search-text-portlet.pt")

    @property
    def macros(self):
        return self.template.macros


class FacetedViewNoTitle(FacetedContainerView):
    """
    """


class ListingGeneric(BrowserView):
    """
    """

    def html2text(self, html):
        if not isinstance(html, basestring):
            return u""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()
        return text

    def cover_url(self, brain):
        url = brain.getURL()
        if url.endswith('index_html'):
            return url[:-len('index_html')]
        return url

    def new_item(self, brain):
        from datetime import datetime

        effective = brain.getObject().effective().asdatetime().date()
        today = datetime.now().date()
        difference = today - effective

        if difference.days > 90:
            return False
        else:
            return True

    def get_publication_date(self, brain):
        obj = brain.getObject()
        date = obj.effective_date

        return portal.get_localized_time(datetime=date).encode('utf-8')
