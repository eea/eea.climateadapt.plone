""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

from Products.Five.browser import BrowserView
from eea.climateadapt.vocabulary import ace_countries
from zope.component.hooks import getSite
from plone.api import portal


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """

    def items(self):
        return self.parent.getFolderContents({'portal_type':'Event', 'sort_by':
                                              'effective'},
                                             full_objects=True)[:3]


class FrontPageCountries(BrowserView):
    """ A view to render the frontpage tile with countries and country select
    form
    """

    def countries(self):
        return ace_countries


class FrontPageCarousel(BrowserView):
    """ A view to render the frontpage carousel
    """

    def items(self):
        site = getSite()
        parent = site['site-news']
        return parent.getFolderContents({'portal_type': 'News Item',
                                         'review_state': 'published',
                                         'sort_by': 'getObjPositionInParent'},
                                        full_objects=True)[:5]


class ListingTile(BrowserView):
    """ Helper for listing tiles on fronpage
    """

    def get_url(self, obj):
        return ""


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

    def items(self):
        return self.parent.getFolderContents({'portal_type': 'News Item',
                                              'sort_by': 'effective'},
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

    def items(self):
        return self.parent.getFolderContents({'portal_type':'Event', 'sort_by':
                                              'effective'},
                                             full_objects=True)[:3]


class LastUpdateTile(BrowserView):
    """ Tile for last update date
    """
    def formated_date(self, modifiedTime):
        return portal.get_localized_time(datetime=modifiedTime)
