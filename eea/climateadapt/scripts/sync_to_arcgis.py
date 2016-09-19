#!/usr/bin/env python

""" A script to sync to arcgis

Note: at this time this module is hackish, being used in developing
and understanding ArcGIS integration.

It has multiple entry points that all do different things:

* Call it from a script such as:

    #!/bin/bash
    export LD_LIBRARY_PATH=../../../../../parts/gdal-compile/lib
    export GISPASS=mypass
    ../../../../../bin/zopepy sync_to_arcgis.py "$@"

This commands accepts various parameter. Look at __main__ to see what it does.

* Call it with its exported console script main():

    bin/www1 run bin/sync_to_arcgis

This connects to Plone to read RabbitMQ server configuration then connects to
RabbitMQ to read all queued messages and process them.
"""

from eea.climateadapt.acemeasure import _measure_id
from functools import partial
import json
import logging
import os
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


def query_layer(token, filter="1=1"):
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


def _arcgis_req(data, op='updates', token=None):
    """ Makes a request to arcgis
    """

    if token is None:
        token_url = get_token_service_url()
        token = generate_token(token_url)

    data = {
        'f': 'json',
        'token': token,
        'referer': REFERER,
        op: data,
    }
    url = "{0}/applyEdits".format(LAYER_URL)
    resp = requests.post(url, data=data)
    res = resp.json()
    return res


def _get_obj_by_measure_id(site, uid):
    from Products.CMFCore.utils import getToolByName
    catalog = getToolByName(site, 'portal_catalog')

    if len(str(uid)) > 6:
        q = {'UID': uid}
    else:
        q = {'acemeasure_id': uid}

    return catalog.searchResults(**q)[0].getObject()


def _get_obj_FID(obj=None, uid=None, token=None):
    """ The "Object ID Field" for the casestudies_pointLayer is "FID".

    Because the casestudies_pointLayer doesn't use Global Ids, we need to
    identify objects by their FID.
    """

    if token is None:
        token_url = get_token_service_url()
        token = generate_token(token_url)

    if obj is not None:
        measureid = _measure_id(obj)
    else:
        measureid = uid

    res = query_layer(filter='measureid={0}'.format(measureid), token=token)

    fid = res['features'][0]['attributes']['FID']
    logger.info("Got FID %s for measureid %s", fid, measureid)
    return fid


# Handlers for events.
def handle_ObjectAddedEvent(site, uid):

    obj = _get_obj_by_measure_id(site, uid)
    entry = obj._repr_for_arcgis()

    token_url = get_token_service_url()
    token = generate_token(token_url)

    entry = json.dumps([entry])
    # TODO: add asserts

    logger.info("ArcGIS: Adding CaseStudy with measure id %s", uid)

    return _arcgis_req(entry, op='adds', token=token)


def handle_ObjectModifiedEvent(site, uid):
    obj = _get_obj_by_measure_id(site, uid)
    repr = obj._repr_for_arcgis()

    token_url = get_token_service_url()
    token = generate_token(token_url)

    fid = _get_obj_FID(obj, token=token)
    repr['attributes']['FID'] = fid

    logger.info("ArcGIS: Updating CaseStudy with FID %s", fid)

    entry = json.dumps([repr])
    res = _arcgis_req(entry, op='updates', token=token)

    assert res['updateResults']
    assert res['updateResults'][0]['objectId'] == fid


def handle_ObjectRemovedEvent(site, uid):
    token_url = get_token_service_url()
    token = generate_token(token_url)

    fid = _get_obj_FID(obj=None, uid=uid, token=token)

    logger.info("ArcGIS: Deleting CaseStudy with FID %s", fid)

    res = _arcgis_req(fid, op='deletes', token=token)

    assert res['deleteResults']
    assert res['deleteResults'][0]['objectId'] == fid


HANDLERS = {
    'ObjectAddedEvent': handle_ObjectAddedEvent,
    'ObjectModifiedEvent': handle_ObjectModifiedEvent,
    'ObjectRemovedEvent': handle_ObjectRemovedEvent,
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


def backup_data(data, path='out.xml'):
    """ Makes an XML backup data from existing data in ArcGIS
    """
    from lxml.etree import Element, SubElement, tostring
    root = Element("casestudies")

    for cs in data:
        e_cs = SubElement(root, 'casestudy')
        e_attrs = SubElement(e_cs, 'attributes')
        for k, v in cs['attributes'].items():
            el = Element(k)
            el.text = unicode(v)
            e_attrs.append(el)
        e_geo = SubElement(e_cs, 'geometry')
        for k, v in cs['geometry'].items():
            el = Element(k)
            el.text = unicode(v)
            e_geo.append(el)

    with open(path, 'w') as f:
        out = tostring(root, pretty_print=True)
        f.write(out)


def delete_casestudy(fid):
    """ Delete a casestudy. To be used from command line
    """
    return _arcgis_req(fid, op='deletes', token=token)


def delete_all_casestudies(token):
    res = query_layer(token)
    all_ids = [x['attributes']['FID'] for x in res['features']]
    return _arcgis_req(all_ids, op='deletes', token=token)


def add_casestudy(entry):
    """ Add a casestudy to ArgGIS
    """
    # return _arcgis_req(entry, op='deletes', token=token)


def parse_dump(path):
    from lxml.etree import fromstring

    with open(path) as f:
        txt = f.read()

    entries = []
    root = fromstring(txt)
    for e_cs in root.xpath('//casestudy'):
        e = {'geometry':{}, 'attributes':{}}
        e_attrs = e_cs.find('attributes')
        e_geo = e_cs.find('geometry')
        for c in e_attrs.iterchildren():
            e['attributes'][c.tag] = (c.text or "").strip()
        for c in e_geo.iterchildren():
            e['geometry'][c.tag] = float(c.text.strip())

        entries.append(e)

    return entries


def edit_casestudy(fid, path, token):
    """ Used from command line
    """
    from lxml.html import fromstring, tostring

    entries = parse_dump(path)
    entry = None
    for e in entries:
        if e['attributes']['FID'] == fid:
            entry = e
            break

    assert entry
    desc = entry['attributes']['desc_']
    html = fromstring(desc)
    desc = tostring(html, encoding='utf-8', method='text').strip()
    entry['attributes']['desc_'] = desc
    res = _arcgis_req(json.dumps([entry]), op='updates', token=token)

    assert 'error' not in res

    return res


def add_all_casestudies(path):
    """ Used from command line
    """
    from lxml.html import fromstring, tostring
    entries = parse_dump(path)

    # need to escape html
    for entry in entries:
        desc = entry['attributes']['desc_']
        html = fromstring(desc)
        desc = tostring(html, encoding='utf-8', method='text').strip()
        entry['attributes']['desc_'] = desc

    res = _arcgis_req(json.dumps(entries), op='adds', token=token)
    return res


if __name__ == "__main__":
    # Needs env vars:
    #     LD_LIBRARY_PATH=<buildout-directory>/parts/gdal-compile/lib
    #     GISPASS=''

    import sys

    token_url = get_token_service_url()
    token = generate_token(token_url)

    if sys.argv[1] == 'url':
        print
        print "Token:", token
        print
        print "Feature URL: ", LAYER_URL + "?token=" + token
        print
        print "Query URL: ", LAYER_URL + "/query?token=" + token
        print

    elif sys.argv[1] == 'dump':
        print "Dumping..."
        if len(sys.argv) > 2:
            path = sys.argv[2]
        else:
            path = 'out.xml'
        res = query_layer(token=token)
        backup_data(res['features'], path=path)

    elif sys.argv[1] == 'summary':
        res = query_layer(token=token)
        print "Summary {0} entries...".format(len(res['features']))
        for entry in res['features']:
            geo = '{0} x {1}'.format(*entry['geometry'].values())
            attr = entry['attributes']
            print attr['FID'], ': ', attr['itemname'], ' @ ', geo

    elif sys.argv[1] == 'del':
        print "Deleting..."
        fid = sys.argv[2]
        res = delete_casestudy(int(fid))
        print res

    elif sys.argv[1] == 'delall':
        print "Deleting all..."
        print delete_all_casestudies(token)

    elif sys.argv[1] == 'addall':
        path = sys.argv[2]
        print add_all_casestudies(path)

    elif sys.argv[1] == 'edit':
        print "Editing..."
        fid = sys.argv[2]
        path = sys.argv[3]
        edit_casestudy(fid, path, token)
    else:
        print "Invalid command"
