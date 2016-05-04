import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class IMapViewerView (Interface):
    """ map-viewer Interface """


class MapViewerView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/tools/map-viewer """

    implements(IMapViewerView)

    def __call__(self):
        return self.request.response.redirect('/tools/map-viewer?' + self.request['QUERY_STRING'])
