""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

import json

from eea.climateadapt.translation.utils import (
    TranslationUtilsMixin, translate_text)
from zope.component.hooks import getSite

from plone.api import portal
from plone.memoize import view
from Products.Five.browser import BrowserView


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """

    def items(self):
        return self.parent.getFolderContents({'portal_type': 'Event',
                                              'sort_by': 'effective'},
                                             full_objects=True)[:3]


class FrontPageCountries(BrowserView, TranslationUtilsMixin):
    """ A view to render the frontpage tile with countries and
        country select form
    """

    def countries(self):
        countries_folder = self.context.unrestrictedTraverse(
            '{}/countries-regions/countries'.format(self.current_lang)
        )

        # countries = [c for c in countries_folder.contentValues()]

        countries = [c.getObject() for c in countries_folder.getFolderContents(
            {
                'sort_on': 'sortable_title',
                'sort_order': 'ascending'
            })]

        res = [(c.getId(), c.Title())
               for c in countries if c.portal_type in \
                   ['Folder', 'collective.cover.content']]

        return res


class ListingTile(BrowserView, TranslationUtilsMixin):
    """ Helper for listing tiles on fronpage
    """


class NewsTile(ListingTile):
    """ Tile for news on frontpage
    """

    title = "News"

    @property
    def more_url(self):
        return [
            self.parent.absolute_url(),
            translate_text(self.context, self.request,
                "More news", 'eea.climateadapt.frontpage', self.current_lang)
        ]

    @property
    def parent(self):
        site = getSite()

        return site[self.current_lang]['news-archive']

    @view.memoize
    def get_item_date(self, item):
        if not item.effective_date:
            return 'No date'

        date = item.effective_date.strftime('%d %b %Y')

        return date

    def get_item_title(self, item):
        name = item.Title()
        if len(name) > 60:
            title = name[:60] + ' ...'
        else:
            title = name

        return title

    @view.memoize
    def get_external_url(self, item):
        url = getattr(item, 'remoteUrl', None)

        if url:
            if url.find('http://') != -1:
                return url
            else:
                return 'http://' + url

        return item.absolute_url()

    def items(self):
        return self.parent.getFolderContents({'portal_type': ['Link',
                                                              'News Item'],
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
        return [
            self.parent.absolute_url(),
            translate_text(self.context, self.request, "More events",
                           'eea.climateadapt.frontpage', self.current_lang)
        ]

    @property
    def parent(self):
        site = getSite()

        return site[self.current_lang]['more-events']

    @view.memoize
    def get_item_date(self, item):
        if not item.effective_date:
            return 'No date'

        try:
            date = item.end.strftime('%d %b %Y')
        except Exception:
            return None
            # TODO Make sure start and end date are copied for all translated
            # events.

        return date

    def get_item_title(self, item):
        name = item.Title()
        if len(name) > 60:
            title = name[:60] + ' ...'
        else:
            title = name

        return title

    @view.memoize
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


class CountriesTileMetadata(BrowserView, TranslationUtilsMixin):
    def __call__(self):
        countries_folder = self.context.unrestrictedTraverse(
            '{}/countries-regions/countries'.format(self.current_lang)
        )

        countries = [c for c in countries_folder.contentValues()]

        res = [c.Title() for c in countries if c.portal_type
               in ['Folder', 'collective.cover.content']]

        return json.dumps(res)
