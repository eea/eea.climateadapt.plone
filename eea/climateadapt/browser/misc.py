from Products.Five.browser import BrowserView
from zope.interface import Interface
from zope.interface import implements


class ISimplifiedResourceRegistriesView(Interface):
    """ A view with simplified resource registries """


class TransRegionView(BrowserView):
    """ Custom view for /transnational-regions """
    implements(ISimplifiedResourceRegistriesView)


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(ISimplifiedResourceRegistriesView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' +
                                              self.request['QUERY_STRING'])


class SatView(BrowserView):
    """ A http://climate-adapt.eea.europa.eu/sat custom view """
    implements(ISimplifiedResourceRegistriesView)


class AdaptationStrategyView (BrowserView):
    """ Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
        to /countries-view-map
    """

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
