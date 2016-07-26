""" A script to sync to arcgis
"""


from Products.CMFCore.utils import getToolByName
from eea.climateadapt.rabbitmq import consume_messages
from eea.climateadapt.scripts import get_plone_site
from functools import partial
import json
import ogr, osr
import requests

USERNAME = "eea_casestudies"
PASSWORD = ""

SERVER_NAME = "LcQjj2sL7Txk9Lag"
ENDPOINT = "http://services.arcgis.com/{0}/ArcGIS/rest".format(SERVER_NAME)
#FEATURE = "casestudies_pointLayer"
FEATURE = "casestudies_pointLayer_clone"
LAYER_URL = "{0}/services/{1}/FeatureServer/0".format(ENDPOINT, FEATURE)

REFERER = 'eea.climateadapt.casestudy'

ARCGIS_EPSG = 3857
GEO_EPSG = 4326     # See Arcgis docs on "Geographic Coordinate Systems"


def get_token_service_url():
    url = ENDPOINT + "/info?f=pjson"
    j = requests.get(url).json()
    return j['authInfo']['tokenServicesUrl']


def generate_token(url):
    data = {
        'f': 'json',
        'username': USERNAME,
        'password': PASSWORD,
        'referer': REFERER,
    }
    resp = requests.post(url, data=data)
    token = resp.json()['token']
    return token


def query_layer(token):
    """ Returns a mapping of 2 members: features and fields

    features is a list of records.
    A record is a dict with an "attributes" record and a "geometry" record.

    Ex:

    {u'features': [{u'attributes': {u'CreationDate': 1465804777348,
                                    u'Creator': u'villamig_ago',
                                    u'EditDate': 1465804777348,
                                    u'Editor': u'villamig_ago',
                                    u'FID': 1,
                                    u'area': u'Atlantic',
                                    u'casestudyf': u'CASESEARCH;',
                                    u'client_cls': u'featured',
                                    u'desc_': u'<p>The Albert canal in the eastern part of Flanders connects the industrial zones around Liege with  ...</p>',
                                    u'featured': u'yes',
                                    u'itemname': u'New locks in Albertkanaal in Flanders, Belgium',
                                    u'measureid': 5601,
                                    u'newitem': u'no',
                                    u'risks': u'DROUGHT;',
                                    u'sectors': u'INFRASTRUCTURE;WATERMANAGEMENT;',
                                    u'website': u'www.descheepvaart.be/english.aspx;www.amice-project.eu/en/amice-project.php?refaction=31;www.madeinkempen.be/nieuws/reusachtige-vijzels-voor-pompinstallatie-aan-sluizencomplex-olen'},
                    u'geometry': {u'x': 560130.5, u'y': 6626173.1}},
                    ...
    u'fields': [{u'alias': u'FID',
                u'defaultValue': None,
                u'domain': None,
                u'name': u'FID',
                u'sqlType': u'sqlTypeInteger',
                u'type': u'esriFieldTypeInteger'},
                ...
    }

    Fields are:
        [u'FID', u'area', u'itemname', u'desc_', u'website', u'sectors',
        u'risks', u'measureid', u'featured', u'newitem', u'casestudyf',
        u'client_cls', u'CreationDate', u'Creator', u'EditDate', u'Editor']
    """
    data = {
        'f': 'json',
        'useGlobalIds': True,
        'where': "1=1",
        #'outFields': 'objectid,itemname,measureid,FID,globalid', #"*"
        'outFields': '*',
        'token': token,
        'referer': REFERER
    }
    url = "{0}/query".format(LAYER_URL)
    resp = requests.get(url, params=data)
    return resp.json()


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


def test_edit(token):
    """ Debugging function, shows how to edit
    """
    data = {
        'f': 'json',
        'token': token,
        'referer': REFERER,
        'features': json.dumps([
            {
                'attributes': {
                    "FID": 48,
                    'itemname': 'test changed by tibi',
                }
            }
        ]),
    }
    url = "{0}/updateFeatures".format(LAYER_URL)
    resp = requests.post(url, data=data)
    return resp.json()


def describe_service(token):
    """ Debugging function. Returns service information
    """

    data = {
        'f': 'json',
        'token': token,
        'referer': REFERER,
    }
    url = "{0}".format(LAYER_URL)
    resp = requests.get(url, params=data)
    return resp.json()


# def main():
#     token_url = get_token_service_url()
#     token = generate_token(token_url)
#     print "Got token:", token
#
#     # pprint(describe_service(token))
#     # return
#
#     test_edit(token)
#
#     results = query_layer(token)
#     pprint(results)
#     # titles = [(f['attributes']['itemname'],
#     #            f['attributes']['measureid'],
#     #            f['attributes']['FID'],
#     #            f['geometry'])
#     #           for f in results['features']]
#     # pprint(titles)
#
#     fields = [r['name'] for r in results['fields']]
#     pprint(fields)
#
#     #test_convert_from_points()


def _get_obj_by_uid(context, uid):
    catalog = getToolByName(context, 'portal_catalog')
    return catalog.searchResults(UID=uid)[0].getObject()


def handle_ObjectAddedEvent(context, uid):
    obj = _get_obj_by_uid(context, uid)
    js = obj._repr_for_arcgis()
    print js


HANDLERS = {
    'ObjectAddedEvent': handle_ObjectAddedEvent,
}


def _consume_msg(*args, **kw):
    """ A closure for consumers. If python had curried functions
    """

    resp, props, msg = args[0]
    context = kw['context']

    eventname, uid = msg.split('|', 1)
    HANDLERS[eventname](context, uid)


def main():
    """ Run the sync import process

    This should be run through the zope client script running machinery, like so:

    bin/www1 run bin/sync_to_arcgis

    It will consume all messages found in the queue and then exit
    """

    site = get_plone_site()
    consume_messages(
        partial(_consume_msg, context=site),
        queue='eea.climateadapt.casestudies'
    )


if __name__ == "__main__":
    main()
