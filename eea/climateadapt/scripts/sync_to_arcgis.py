#!/usr/bin/env python

""" A script to sync to arcgis
"""

from eea.climateadapt.acemeasure import _measure_id
from functools import partial
import json
import logging
import ogr
import os
import osr
import requests

logger = logging.getLogger('eea.climateadapt.arcgis')


USERNAME = "eea_casestudies"
PASSWORD = os.environ.get('GISPASS', "")

SERVER_NAME = "LcQjj2sL7Txk9Lag"
ENDPOINT = "http://services.arcgis.com/{0}/ArcGIS/rest".format(SERVER_NAME)
#FEATURE = "casestudies_pointLayer"
FEATURE = "casestudies_pointLayer_clone"
LAYER_URL = "{0}/services/{1}/FeatureServer/0".format(ENDPOINT, FEATURE)

REFERER = 'climate-adapt.europa.eu CaseStudies Sync'

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


def query_layer(token=None, filter="1=1"):
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
        'where': filter,
        # 'outFields': 'objectid,itemname,measureid,FID,globalid', #"*"
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


def _arcgis_req(entry, op='updates', token=None):

    if token is None:
        token_url = get_token_service_url()
        token = generate_token(token_url)

    data = {
        'f': 'json',
        'token': token,
        'referer': REFERER,
        op: json.dumps([entry]),
    }
    url = "{0}/applyEdits".format(LAYER_URL)
    resp = requests.post(url, data=data)
    res = resp.json()
    return res


def arcgis_add_entry(entry, token=None):
    return _arcgis_req(entry, op='adds', token=token)


def arcgis_del_entry(entry, token=None):
    return _arcgis_req(entry, op='deletes', token=token)


def arcgis_edit_entry(entry, token=None):
    return _arcgis_req(entry, op='updates', token=token)


def _get_obj_by_measure_id(site, uid):
    from Products.CMFCore.utils import getToolByName
    catalog = getToolByName(site, 'portal_catalog')

    if len(str(uid)) > 6:
        q = {'UID': uid}
    else:
        q = {'acemeasure_id': uid}

    return catalog.searchResults(**q)[0].getObject()


def _get_obj_FID(obj, token=None):
    """ The "Object ID Field" for the casestudies_pointLayer is "FID".

    Because the casestudies_pointLayer doesn't use Global Ids, we need to
    identify objects by their FID.
    """

    if token is None:
        token_url = get_token_service_url()
        token = generate_token(token_url)

    measureid = _measure_id(obj)
    res = query_layer(filter='measureid={0}'.format(measureid), token=token)

    fid = res['features'][0]['attributes']['FID']
    logger.info("Got FID %s for measureid %s", fid, measureid)
    return fid


# Handlers for events.
def handle_ObjectAddedEvent(site, uid):
    import pdb; pdb.set_trace()

    obj = _get_obj_by_measure_id(site, uid)
    entry = obj._repr_for_arcgis()

    token_url = get_token_service_url()
    token = generate_token(token_url)
    arcgis_add_entry(entry, token=token)

    # TODO: ???

def handle_ObjectModifiedEvent(site, uid):
    obj = _get_obj_by_measure_id(site, uid)
    repr = obj._repr_for_arcgis()

    token_url = get_token_service_url()
    token = generate_token(token_url)

    fid = _get_obj_FID(obj, token=token)
    repr['attributes']['FID'] = fid
    res = arcgis_edit_entry(repr, token=token)

    assert res['updateResults']
    assert res['updateResults'][0]['objectId'] == fid


def handle_ObjectWillBeRemovedEvent(site, uid):
    # TODO: ???
    obj = _get_obj_by_measure_id(site, uid)
    repr = obj._repr_for_arcgis()

    import pdb; pdb.set_trace()
    fid = _get_obj_FID(obj, token=token)
    repr['attributes']['FID'] = fid
    res = arcgis_del_entry(repr, token=token)

    assert res['deleteResults']
    assert res['deleteResults'][0]['objectId'] == fid


HANDLERS = {
    'ObjectAddedEvent': handle_ObjectAddedEvent,
    'ObjectModifiedEvent': handle_ObjectModifiedEvent,
    'ObjectWillBeRemovedEvent': handle_ObjectWillBeRemovedEvent,
}


def _consume_msg(*args, **kw):
    """ Consume RabbitMQ messages. Dispatches to proper handler
    """

    resp, props, msg = args[0]
    context = kw['context']

    eventname, uid = msg.split('|', 1)
    HANDLERS[eventname](context, uid)


def main():
    """ Run the sync import process

    This should be run through the zope client script running machinery, like so:

    GISPASS="..." bin/www1 run bin/sync_to_arcgis

    It will consume all messages found in the queue and then exit
    """

    from eea.climateadapt.rabbitmq import consume_messages
    from eea.climateadapt.scripts import get_plone_site

    site = get_plone_site()
    consume_messages(
        partial(_consume_msg, context=site),
        queue='eea.climateadapt.casestudies'
    )


if __name__ == "__main__":
    # Needs env vars:
    #     LD_LIBRARY_PATH=<buildout-directory>/parts/gdal-compile/lib
    #     GISPASS=''

    token_url = get_token_service_url()
    token = generate_token(token_url)

    import sys
    if sys.argv[1] == 'url':
        print "Token:", token
        print "Feature URL: ", LAYER_URL + "?token=" + token
    elif sys.argv[1] == 'dump':
        print "Dumping..."
        res = query_layer(token=token)
        import pdb;pdb.set_trace()
