""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

import json

# from eea.climateadapt.translation.utils import (
#     TranslationUtilsMixin, translate_text)

# from collective.cover.tiles.base import (IPersistentCoverTile,
#                                          PersistentCoverTile)
# from zope import schema
from zope.component.hooks import getSite
# from zope.interface import implements

# from plone import api
from plone.api import portal
# from plone.app.textfield import RichText
from plone.memoize import view
# from plone.namedfile.field import NamedBlobImage
# from plone.tiles.interfaces import ITileDataManager
from Products.Five.browser import BrowserView


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """

    def items(self):
        return self.parent.getFolderContents({'portal_type': 'Event',
                                              'sort_by': 'effective'},
                                             full_objects=True)[:3]


# TODO add TranslationUtilsMixin to inheritance
class FrontPageCountries(BrowserView):
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


# class ICarousel(IPersistentCoverTile):
#     """ Frontpage carousel tile schema """
#     # form.fieldset('slide1',
#     #               label=u'Slide 1',
#     #               fields=['s1_title', 's1_description', 's1_primary_photo',
#     #                       's1_photo_copyright', 's1_read_more_text',
#     #                       's1_read_more_link']
#     #               )

#     form.fieldset('slide2',
#                   label='Slide 1',
#                   fields=['s2_title', 's2_description', 's2_primary_photo',
#                           's2_read_more_text', 's2_read_more_link']
#                   )

#     form.fieldset('slide8',
#                   label='Slide 2',
#                   fields=['s8_title', 's8_description', 's8_primary_photo',
#                           's8_read_more_text', 's8_read_more_link']
#                   )

#     form.fieldset('slide5',
#                   label='Slide 5',
#                   fields=['s5_title', 's5_description', 's5_primary_photo',
#                           's5_read_more_text', 's5_read_more_link']
#                   )

#     form.fieldset('slide7',
#                   label='Slide 7',
#                   fields=['s7_title', 's7_description', 's7_primary_photo',
#                           's7_read_more_text', 's7_read_more_link']
#                   )

#     # Slide 1 fields
#     # s1_title = schema.Text(title=u"First slide Title", required=True)
#     # s1_description = RichText(title=u"First slide description",
#     # required=False)

#     # s1_primary_photo = NamedBlobImage(
#     #     title=(u"First Slide Photo"),
#     #     required=False,
#     # )

#     # s1_photo_copyright = schema.Text(title=u"Photo Copyright", required=True)

#     # s1_read_more_text = schema.Text(title=u"First slide read more text",
#     #                                 required=False)
#     # s1_read_more_link = schema.Text(title=u"First slide read more link",
#     #                                 required=False)

#     # Slide 2 fields
#     s2_title = schema.Text(title="Second slide Title", required=True)
#     s2_description = RichText(title="Second slide description",
#                               required=False)

#     s2_primary_photo = NamedBlobImage(
#         title=("Second Slide Photo"),
#         required=True,
#     )

#     s2_read_more_text = schema.Text(title="Second slide read more text",
#                                     required=False)
#     s2_read_more_link = schema.Text(title="Second slide read more link",
#                                     required=False)

#     # Slide 5 fields
#     s5_title = schema.Text(title="Fifth slide title", required=True)
#     s5_description = RichText(title="Fifth slide text", required=False)

#     s5_primary_photo = NamedBlobImage(
#         title=("Fifth slide photo"),
#         required=True,
#     )

#     s5_read_more_text = schema.Text(title="Fifth slide read more text",
#                                     required=False)
#     s5_read_more_link = schema.Text(title="Fifth slide read more link",
#                                     required=False)

#     # Slide 7 fields
#     s7_title = schema.Text(title="Seventh slide title", required=True)
#     s7_description = RichText(title="Seventh slide text", required=False)

#     s7_primary_photo = NamedBlobImage(
#         title=("Seventh slide photo"),
#         required=True,
#     )

#     s7_read_more_text = schema.Text(title="Seventh slide read more text",
#                                     required=False)
#     s7_read_more_link = schema.Text(title="Seventh slide read more link",
#                                     required=False)

#     # Slide 8 fields
#     s8_title = schema.Text(title="Slide title", required=True)
#     s8_description = RichText(title="Slide text", required=False)

#     s8_primary_photo = NamedBlobImage(
#         title=("Slide photo"),
#         required=True,
#     )

#     s8_read_more_text = schema.Text(title="Slide read more text",
#                                     required=False)
#     s8_read_more_link = schema.Text(title="Slide read more link",
#                                     required=False)


# class Carousel(PersistentCoverTile):
#     """ Frontpage Carousel tile
#     """
#     implements(ICarousel)

#     is_configurable = True
#     is_editable = True
#     is_droppable = False
#     ignoreContext = False
#     short_name = 'eea.carousel.tile'

#     def get_tile(self, slide_id):
#         tile = ITileDataManager(self)
#         data = tile.annotations[tile.key]

#         for key in list(data.keys()):
#             if slide_id in key:
#                 setattr(self, key, data.get(key, ''))

#         return self

#     def get_image(self, image, fieldname):
#         url = self.context.absolute_url() + '/@@edit-tile/' + self.short_name
#         url += '/{0}/++widget++{1}.{2}'.format(self.id, self.short_name,
#                                                fieldname)
#         # '/' + self.id + '/++widget++' + self.short_name + '.' + fieldname
#         url += '/@@download/' + image.filename

#         return url

#     def news_items(self):
#         """ Gets the most recent updated news/events item"""
#         site = getSite()
#         catalog = site.portal_catalog
#         result = catalog.searchResults({'portal_type': ['News Item', 'Event'],
#                                         'review_state': 'published',
#                                         'sort_on': 'effective',
#                                         'sort_order': 'reverse'},
#                                        full_objects=True)[0]

#         return result.getObject()

#     def last_casestudy(self):
#         """ Gets the most recent updated casestudy"""
#         site = getSite()
#         catalog = site.portal_catalog
#         brain = catalog.searchResults({
#             'portal_type': 'eea.climateadapt.casestudy',
#             'review_state': 'published',
#             'sort_on': 'effective',
#             'sort_order': 'descending',
#         }, full_objects=True)[0]

#         cs = brain.getObject()

#         return {
#             'image':
#             "{0}/@@images/primary_photo/?c={1}".format(
#                 cs.absolute_url(),
#                 brain.modified and brain.modified.ISO() or ''
#             ),
#             'title': cs.Title(),
#             'description': self.html2text(cs.long_description.output),
#             'url': cs.absolute_url(),

#         }

#     @view.memoize
#     def html2text(self, html):
#         if not isinstance(html, str):
#             return ""
#         portal_transforms = api.portal.get_tool(name='portal_transforms')
#         data = portal_transforms.convertTo('text/plain',
#                                            html, mimetype='text/html')
#         text = data.getData()

#         return text

#     def last_dbitem(self):
#         """ Gets the most recent updated aceitem"""
#         site = getSite()
#         catalog = site.portal_catalog
#         result = catalog.searchResults({
#             'portal_type': [
#                 'eea.climateadapt.informationportal',
#                 'eea.climateadapt.guidancedocument',
#                 'eea.climateadapt.tool',
#                 'eea.climateadapt.mapgraphdataset',
#                 'eea.climateadapt.indicator',
#                 'eea.climateadapt.organisation'
#             ],
#             'review_state': 'published',
#             'sort_by': 'effective'}, full_objects=True)[0]

#         return result.getObject()

#     def last_publication(self):
#         """ Gets the most recent updated publication and report"""
#         site = getSite()
#         catalog = site.portal_catalog
#         result = catalog.searchResults({
#             'portal_type': 'eea.climateadapt.publicationreport',
#             'review_state': 'published',
#             'sort_on': 'effective',
#             'sort_order': 'descending',
#         }, full_objects=True)[0]

#         return result.getObject()


# TODO add TranslationUtilsMixin to inheritance
class ListingTile(BrowserView):
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
            "More news"
            # translate_text(self.context, self.request,
            #     "More news", 'eea.climateadapt.frontpage', self.current_lang)
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
            "More news"
            # translate_text(self.context, self.request, "More events",
            #                'eea.climateadapt.frontpage', self.current_lang)
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


# TODO add TranslationUtilsMixin to inheritance
class CountriesTileMetadata(BrowserView):
    def __call__(self):
        countries_folder = self.context.unrestrictedTraverse(
            '{}/countries-regions/countries'.format(self.current_lang)
        )

        countries = [c for c in countries_folder.contentValues()]

        res = [c.Title() for c in countries if c.portal_type
               in ['Folder', 'collective.cover.content']]

        return json.dumps(res)
