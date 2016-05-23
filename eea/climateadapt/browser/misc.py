import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView
from plone.app.contenttypes.browser.folder import FolderView


class ITransRegionView (Interface):
    """ Transnational regions Interface """


class IMapViewerView (Interface):
    """ map-viewer Interface """


class ICountriesView (Interface):
    """ Countries Interface """


class ICitiesProfilesView(Interface):
    """ City Profiles Interface """


class IAdaptationStrategy (Interface):
    """ Adaptation Interface """


class TransRegionView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/transnational-regions """

    implements(ITransRegionView)


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(IMapViewerView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' + self.request['QUERY_STRING'])


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """

    implements(ICountriesView)


class CitiesProfilesView(FolderView):
    """ Custom view for  city-profiles"""

    implements(ICitiesProfilesView)


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
