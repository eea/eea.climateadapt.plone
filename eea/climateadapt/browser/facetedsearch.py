# -*- coding: utf-8 -*-

""" Utilities for faceted search
"""

from collections import defaultdict
from datetime import datetime

from eea.cache import cache
from eea.facetednavigation.browser.app.view import FacetedContainerView
from eea.facetednavigation.caching.cache import cacheKeyFacetedNavigation
from plone import api
from plone.api import portal
from Products.CMFPlone.utils import isExpired
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# from zope.annotation.interfaces import IAnnotations

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
    # ("VIDEOS", "Videos"),
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
    # ("VIDEOS", "Videos"),
]

CCA_TYPES = [
    'eea.climateadapt.adaptationoption',
    'eea.climateadapt.aceproject',
    'eea.climateadapt.casestudy',
    'eea.climateadapt.guidancedocument',
    'eea.climateadapt.indicator',
    'eea.climateadapt.informationportal',
    'eea.climateadapt.mapgraphdataset',
    'eea.climateadapt.organisation',
    'eea.climateadapt.publicationreport',
    'eea.climateadapt.researchproject',
    'eea.climateadapt.tool',
    'eea.climateadapt.city_profile',
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

    def key(method, self, name, brains):
        print "caching ", name

        cache_key = cacheKeyFacetedNavigation(method, self, name, brains)
        cache_key += (name, )

        return cache_key

    @cache(key, dependencies=['eea.facetednavigation'])  # , lifetime=36000
    def render(self, name, brains):
        print "rendering ", name

        # if name != 'DOCUMENT':
        #     return ''

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
    """ This view is (re)used to render each faceted section in search results
    """

    # def key(method, self):
    #     site = api.portal.getSite()
    #     portal_type = self.brains[0].getObject().portal_type

    #     cache_key = cacheKeyFacetedNavigation(method, self)
    #     cache_key += (portal_type, )

    #     if not IAnnotations(site).get('cca-search', None):
    #         IAnnotations(site)['cca-search'] = {}

    #     if portal_type not in CCA_TYPES:
    #         if not IAnnotations(site)['cca-search'].get('CONTENT', None):
    #             IAnnotations(site)['cca-search']['CONTENT'] = []
    #         IAnnotations(site)['cca-search']['CONTENT'].append(cache_key)
    #     else:
    #         if not IAnnotations(site)['cca-search'].get(portal_type, None):
    #             IAnnotations(site)['cca-search'][portal_type] = []
    #         IAnnotations(site)['cca-search'][portal_type].append(cache_key)

    #     print "caching ", portal_type
    #     return cache_key

    # @cache(key, lifetime=36000)
    # def __call__(self):
    #     return self.index()

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
        if brain.portal_type in ['News Item', 'Link', 'Event']:
            return False

        date = brain.effective
        effective = date.asdatetime().date()
        today = datetime.now().date()
        difference = today - effective

        if difference.days > 90:
            return False
        else:
            return True

    def get_publication_date(self, brain):
        date = brain.effective

        if date.year() == 1969:
            return ''
        # date = obj.effective_date

        return portal.get_localized_time(datetime=date).encode('utf-8')

    def expired(self, brain):
        if brain.portal_type not in ['News Item', 'Link', 'Event']:
            return False

        if isExpired(brain) == 1:
            return True

        return False


_IMG_FEATURED = u"""<img
src="++theme++climateadapt/static/cca/img/featured-icon.png" />"""
_IMG_NEW = u"""<img src="++theme++climateadapt/static/cca/img/new-en.gif" />"""


class BaseSectionRenderer(ListingGeneric):
    """ Base class for rendering sections in faceted search
    """

    def key(method, self, brain):
        return 'row-' + brain.UID

    # @cache(key)
    def render_row(self, brain):
        ld = getattr(brain.long_description, 'raw', brain.long_description)

        if isinstance(ld, str):
            ld = ld.decode('utf-8')

        text = self.html2text(ld)
        title = brain.Title.decode('utf-8')
        img_featured = brain.featured == 1 and _IMG_FEATURED or ''
        img_new = self.new_item(brain) and _IMG_NEW or ''

        values = {
            'title': title,
            'img_featured': img_featured,
            'img_new': img_new,
            'url': brain.getURL(),
            'text': text[:208-len(title)],
            'year': brain.year or ' ',
            'pub_date': self.get_publication_date(brain)
        }

        return self._TEMPLATE_ROW.format(**values)

    def __call__(self):
        rows = []

        for brain in self.brains:
            row = self.render_row(brain)
            rows.append(row)

        rows = u"".join(rows)
        values = {
            "rows": rows,
        }

        return self._TEMPLATE.format(**values)


class FacetedListingGeneric(BaseSectionRenderer):
    """ Rendering the Publication and Reports section
    """

    _TEMPLATE_ROW = u"""
<tr>
<td>
» {img_featured}
{img_new}
<a href="{url}">{title}</a>
- <span >
{text}
</span>
</td>
<td class="table_year_css">{year}</td>
<td class="table_date_css">{pub_date}</td>
</tr>
"""

    _TEMPLATE = u"""
<table class="listing-table">
  <thead>
    <tr>
      <th>Title</th>
      <th>Year</th>
      <th>Published</th>
    </tr>
  </thead>
  <tbody>
  {rows}
  </tbody>
</table>
"""


class FacetedListingNoYear(BaseSectionRenderer):
    """ Same as generic, but misses the Year column
    """

    _TEMPLATE_ROW = u"""
<tr>
<td>
» {img_featured}{img_new}
<a href="{url}">{title}</a> - <span>{text}</span>
</td>
<td class="table_date_css">{pub_date}</td>
</tr>
"""

    _TEMPLATE = u"""
<table class="listing-table">
  <thead>
    <tr>
      <th>Title</th>
      <th>Published</th>
    </tr>
  </thead>
  <tbody>
  {rows}
  </tbody>
</table>
"""
