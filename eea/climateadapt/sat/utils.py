from plone.api.portal import get_tool
from Products.CMFCore.utils import getToolByName

try:
    import ogr
    import osr
except ImportError:
    from osgeo import ogr
    from osgeo import osr


ARCGIS_EPSG = 3857
GEO_EPSG = 4326     # See Arcgis docs on "Geographic Coordinate Systems"


def _transform_coords(x, y, insys, outsys):
    """ Converts a pair of points between two system of coordinates
    """

    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(insys)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outsys)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(x, y)
    point.Transform(coordTransform)

    return (point.GetX(), point.GetY())


def to_arcgis_coords(lat, lon):
    """ Converts from lat/lon coordinates to ArcGIS coordinates

    >>> x = -318130.9
    >>> y = 7116746

    >>> (lat, lon) = to_geo_coords(x, y)
    >>> xc, yc = to_arcgis_coords(lat, lon)
    >>> assert xc == x
    >>> assert yc == y
    """

    return _transform_coords(lat, lon, GEO_EPSG, ARCGIS_EPSG)


def to_geo_coords(x, y):
    """ Converts from ArcGIS coordinates to lat/long pair
    """

    return _transform_coords(x, y, ARCGIS_EPSG, GEO_EPSG)


def _get_obj_by_measure_id(site, uid):
    catalog = getToolByName(site, 'portal_catalog')

    if len(str(uid)) > 6:
        q = {'UID': uid}
    else:
        q = {'acemeasure_id': uid}

    return catalog.searchResults(**q)[0].getObject()


def _measure_id(obj):
    """ Returns the measureid of casestudy as PK for gis operations

    If the object doesn't have a measureid, it assigns a new one
    """

    mid = getattr(obj, '_acemeasure_id', None)

    if mid:
        return mid

    catalog = get_tool(name='portal_catalog')
    ids = sorted([
        _f for _f in catalog.uniqueValuesFor('acemeasure_id')
        if _f])
    obj._acemeasure_id = ids[-1] + 1
    obj.reindexObject(idxs=['acemeasure_id'])

    return obj._acemeasure_id
