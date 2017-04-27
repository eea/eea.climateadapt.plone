""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

from Products.Five.browser import BrowserView
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt.vocabulary import ace_countries_selection
from plone import api
from plone.api import portal
from plone.app.textfield import RichText
from plone.namedfile.field import NamedBlobImage
from plone.tiles.interfaces import ITileDataManager
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements
from plone.memoize import view


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


class ICarousel(IPersistentCoverTile):
    """ Frontpage carousel tile schema """

    # Slide 1 fields
    # s1_title = schema.Text(title=u"First slide Title", required=True)
    # s1_description = RichText(title=u"First slide description", required=False)

    # s1_primary_photo = NamedBlobImage(
    #     title=(u"First Slide Photo"),
    #     required=False,
    # )

    # s1_photo_copyright = schema.Text(title=u"Photo Copyright", required=True)

    # s1_read_more_text = schema.Text(title=u"First slide read more text",
    #                                 required=False)
    # s1_read_more_link = schema.Text(title=u"First slide read more link",
    #                                 required=False)

    # Slide 2 fields
    s2_title = schema.Text(title=u"First slide Title", required=True)
    s2_description = RichText(title=u"First slide description", required=False)

    s2_primary_photo = NamedBlobImage(
        title=(u"First Slide Photo"),
        required=True,
    )

    s2_read_more_text = schema.Text(title=u"First slide read more text",
                                    required=False)
    s2_read_more_link = schema.Text(title=u"First slide read more link",
                                    required=False)

    # Slide 5 fields
    s5_title = schema.Text(title=u"Fifth slide title", required=True)
    s5_description = RichText(title=u"Fifth slide text", required=False)

    s5_primary_photo = NamedBlobImage(
        title=(u"Fifth slide photo"),
        required=True,
    )

    s5_read_more_text = schema.Text(title=u"Fifth slide read more text",
                                    required=False)
    s5_read_more_link = schema.Text(title=u"Fifth slide read more link",
                                    required=False)


class Carousel(PersistentCoverTile):
    """ Frontpage Carousel tile
    """
    implements(ICarousel)

    is_configurable = True
    is_editable = True
    is_droppable = False
    ignoreContext = False
    short_name = 'eea.carousel.tile'

    def get_tile(self, slide_id):
        tile = ITileDataManager(self)
        data = tile.annotations[tile.key]

        for key in data.keys():
            if slide_id in key:
                setattr(self, key, data.get(key, ''))
        return self

    def get_image(self, image, fieldname):
        url = self.context.absolute_url() + '/@@edit-tile/' + self.short_name
        url += '/' + self.id + '/++widget++' + self.short_name + '.' + fieldname
        url += '/@@download/' + image.filename
        return url

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

    @view.memoize
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

    @view.memoize
    def get_item_date(self, item):
        date = item.effective_date.strftime('%d %b %Y')
        return date

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

    @view.memoize
    def get_item_date(self, item):
        date = item.end.strftime('%d %b %Y')
        return date

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
