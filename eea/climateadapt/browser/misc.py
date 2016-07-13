from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView
import json


class ITransRegionView (Interface):
    """ Transnational regions Interface """


class IMapViewerView (Interface):
    """ map-viewer Interface """


class ICountriesView (Interface):
    """ Countries Interface """


class IAdaptationStrategy (Interface):
    """ Adaptation Interface """


class TransRegionView (BrowserView):
    """ Custom view for /transnational-regions """

    implements(ITransRegionView)


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """

    implements(ICountriesView)


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(IMapViewerView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' +
                                              self.request['QUERY_STRING'])


class AdaptationStrategyView (BrowserView):
    """ Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
        to /countries-view-map
    """

    implements(IAdaptationStrategy)

    def __call__(self):
        return self.request.response.redirect('/countries')


class RedirectToSearchView (BrowserView):
    """ Custom view for /content """

    def __call__(self):
        type_name = self.context.getProperty('search_type_name', '')
        url = '/data-and-downloads'
        if type_name:
            url += '#searchtype=' + type_name

        return self.request.response.redirect(url)


class ListTilesWithTitleView (BrowserView):
    """ View that lists all tiles with richtext title and their respective urls
    """

    def __call__(self):
        covers = self.context.portal_catalog.searchResults(
                              portal_type='collective.cover.content')
        self.urls = []
        for cover in covers:
            cover = cover.getObject()

            self.tiles = []

            self.walk(json.loads(cover.cover_layout))

            if hasattr(cover, '__annotations__'):
                for tile_id in self.tiles:
                    tile_id = tile_id.encode()
                    #tile = cover.__annotations__['plone.tiles.data.' + tile_id]
                    self.urls.append(cover.absolute_url())

        return self.index()

    def linkify(self, text):
        if not text:
            return

        if text.startswith('/') or text.startswith('http'):
            return text

        return "http://" + text

    def walk(self, item):
        if isinstance(item, dict):
            if item.get('tile-type') == 'eea.climateadapt.richtext_with_title':
                self.tiles.append(item['id'])

            self.walk(item.get('children', []))
        elif isinstance(item, list):
            for x in item:
                self.walk(x)
