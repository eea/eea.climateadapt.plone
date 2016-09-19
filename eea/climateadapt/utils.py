""" Generic utilities
"""

import ogr
import osr
import time

def _unixtime(d):
    """ Converts a datetime to unixtime
    """

    try:
        return int(time.mktime(d.utctimetuple()))
    except AttributeError:
        return ""


def shorten(t, to=254):
    """ Shortens text and adds elipsis
    """

    if isinstance(t, unicode):
        el = u'...'
    else:
        el = '...'
    if len(t) > to-3:
        t = t[:to-3] + el
    return t


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
