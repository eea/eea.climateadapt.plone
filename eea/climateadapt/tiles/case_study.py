from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.interface import implements


class ICaseStudy(IPersistentCoverTile):
    """
    Case study locator
    """

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )
    proxy_url = schema.TextLine(
        title=_(u'Proxy url'),
        required=True,
        default=u'/proxy/url=',
        )
    geoserver_url = schema.URI(
        title=_("Geoserver url"),
        required=True,
        default='http://ace.geocat.net/geoserver/',
        )
    wms = schema.TextLine(
        title=_("Wms"),
        required=True,
        default=u'wms',
        )
    wfs = schema.TextLine(
        title=_("Wfs"),
        required=True,
        default=u'wfs',
        )
    feature_namespace = schema.URI(
        title=_("Feature namespace"),
        required=True,
        default='http://climate-adapt.eea.europa.eu',
        )
    areas_feature_type = schema.TextLine(
        title=_("Areas feature type"),
        required=True,
        default=u'biogeo_2005',
        )
    areas_layer = schema.TextLine(
        title=_("Areas layer layer"),
        required=True,
        default=u'chm:biogeo_2005',
        )
    case_studies_feature_type = schema.TextLine(
        title=_("Case studies feature type"),
        required=True,
        default=u'casestudies',
        )
    geometry_column = schema.TextLine(
        title=_("Geometry column"),
        required=True,
        default=u'geom',
        )
    area_column = schema.TextLine(
        title=_("Area column"),
        required=True,
        default=u'area',
        )
    locator_url = schema.URI(
        title=_("Locator url"),
        required=True,
        default='http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer',
        )
    locator_key = schema.TextLine(
        title=_("Locator key"),
        required=True,
        default=u'Ao9qujBzDtg-nFiusTjt5VQ9x2NJB2wAD7YCRjaPz7hQQjxdFcl24tyhOwCDCIrw',
        )
    zoom_level = schema.TextLine(
        title=_("Zoom level"),
        required=True,
        default=u'2',
        )


class CaseStudy(PersistentCoverTile):
    """
    Case study locator
    """

    implements(ICaseStudy)

    index = ViewPageTemplateFile('pt/case_study.pt')
