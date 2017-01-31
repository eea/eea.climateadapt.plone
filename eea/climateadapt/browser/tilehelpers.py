""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

from Products.Five.browser import BrowserView
from eea.climateadapt.vocabulary import ace_countries_selection
from zope.component.hooks import getSite
from plone.api import portal
from plone import api


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """

    def items(self):
        return self.parent.getFolderContents({'portal_type': 'Event',
                                              'sort_by': 'effective'},
                                             full_objects=True)[:3]


class FrontPageCountries(BrowserView):
    """ A view to render the frontpage tile with countries and country select
    form
    """

    def countries(self):
        return ace_countries_selection


class FrontPageCarousel(BrowserView):
    """ A view to render the frontpage carousel
    """

    def news_items(self):
        """ Gets the most recent updated news/events item"""
        site = getSite()
        catalog = site.portal_catalog
        result = catalog.searchResults({'portal_type': ['News Item', 'Event'],
                                        'review_state': 'published',
                                        'sort_by': 'effective'},
                                       full_objects=True)[0]
        return result.getObject()

    def last_casestudy(self):
        """ Gets the most recent updated casestudy"""
        site = getSite()
        catalog = site.portal_catalog
        result = catalog.searchResults({
            'portal_type': 'eea.climateadapt.casestudy',
            'review_state': 'published',
            'sort_by': 'effective'}, full_objects=True)[0]

        return result.getObject()

    def html2text(self, html):
        if not isinstance(html, basestring):
            return u""
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/plain',
                                           html, mimetype='text/html')
        text = data.getData()
        return text

    def last_dbitem(self):
        """ Gets the most recent updated aceitem"""
        site = getSite()
        catalog = site.portal_catalog
        result = catalog.searchResults({
            'portal_type': [
                'eea.climateadapt.publicationreport',
                'eea.climateadapt.informationportal',
                'eea.climateadapt.guidancedocument',
                'eea.climateadapt.tool',
                'eea.climateadapt.mapgraphdataset',
                'eea.climateadapt.indicator',
                'eea.climateadapt.organisation'
            ],
            'review_state': 'published',
            'sort_by': 'effective'}, full_objects=True)[0]

        return result.getObject()


class ListingTile(BrowserView):
    """ Helper for listing tiles on fronpage
    """


class NewsTile(ListingTile):
    """ Tile for news on frontpage
    """

    title = "News"

    @property
    def more_url(self):
        return [self.parent.absolute_url(), "More news"]

    @property
    def parent(self):
        site = getSite()
        return site['news-archive']

    def get_item_date(self, item):
        date = item.effective_date.strftime('%d %b %Y')
        return date

    def get_external_url(self, item):
        url = getattr(item, 'remoteUrl', None)
        if url:
            if url.find('http://') != -1:
                return url
            else:
                return 'http://' + url
        return item.absolute_url()

    def items(self):
        return self.parent.getFolderContents({'portal_type': ['Link', 'News Item'],
                                              'sort_on': 'effective',
                                              "sort_order": "reverse",
                                              'review_state': 'published',
                                              },
                                             full_objects=True)[:3]


class EventsTile(ListingTile):
    """ Tile for events on frontpage
    """

    title = "Events"

    @property
    def more_url(self):
        return [self.parent.absolute_url(), "More Events"]

    @property
    def parent(self):
        site = getSite()
        return site['more-events']

    def get_item_date(self, item):
        date = item.end.strftime('%d %b %Y')
        return date

    def get_external_url(self, item):
        url = item.event_url
        if url == '':
            url = item.absolute_url()

        return url

    def items(self):
        return self.parent.getFolderContents({'portal_type': 'Event',
                                              'review_state': 'published',
                                              "sort_order": "reverse",
                                              'sort_on': 'effective'},
                                             full_objects=True)[:3]


class LatestUpdatesTile(ListingTile):
    """ Tile for latest-updates on fp
    """


class LastUpdateTile(BrowserView):
    """ Tile for last update date
    """
    def formated_date(self, modifiedTime):
        return portal.get_localized_time(datetime=modifiedTime)
