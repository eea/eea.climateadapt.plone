import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class ISatOldView(Interface):
    """ An old Marker interface ISatView"""


class SatOldView(BrowserView):
    """ The old http://climate-adapt.eea.europa.eu/sat custom view """
    implements(ISatOldView)

    INLINE_JS = """
    var proxyUrl = '';
    var geoserverUrl = '{geoserver_url}';
    var wfs = '{wms}';
    var wms = '{wfs}';
    var featureNamespace = '{feature_namespace}';
    var areasFeatureType = '{feature_type}';
    var areasLayer = '{areas_layer}';
    var caseStudiesFeatureType = '{casestudies_feature_type}';
    var geometryColumn = '{geometry_col}';
    var areaColumn = '{area_col}';
    var locatorUrl = '{locator_url}';
    var locatorKey = '{locator_key}';
    var zoomLevel = {initial_zoom_level};
    var root = '{js_root}';"""

    def js_settings(self):
        js_settings = {
            'geoserver_url': 'http://climate-adapt.eea.europa.eu/geoserver/',
            'wfs': 'wfs',
            'wms': 'wms',
            'feature_namespace': 'http://climate-adapt.eea.europa.eu',
            'feature_type': 'biogeo_2008',
            'areas_layer': 'chm:biogeo_2008',
            'casestudies_feature_type': 'casestudies',
            'geometry_col': 'geom',
            'area_col': 'area',
            'locator_url': (
                'http://geocode.arcgis.com/arcgis/rest/'
                'services/World/GeocodeServer/'
            ),
            'locator_key': ('AgyLk7bO8WrzknvPFCGPq-fhUvYnQhoZgK74Mvt-'
                            'i9wRTkDTv1nDzFs-D5LnGNAN'),
            'initial_zoom_level': 2,
            'js_root': '++resource++eea.climateadapt/SimilarAreasTool-portlet/'
        }
        if os.environ.get('CORS_PROXY_DEVEL'):
            js_settings['geoserver_url'] = '{cors_proxy}/{url}'.format(
                cors_proxy=os.environ['CORS_PROXY_DEVEL'],
                url=js_settings['geoserver_url'].split('//')[1]
            )
        return js_settings

    @property
    def inline_js(self):
        js_settings = self.js_settings()
        return self.INLINE_JS.format(**js_settings)
