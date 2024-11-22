""" Settings, utilities to integrate with the ArcGIS server, for the SAT tool
"""

import logging

import requests

from eea.climateadapt.sat.settings import (get_endpoint_url, get_feature_url,
                                           get_settings)
from eea.climateadapt.sat.utils import _measure_id

logger = logging.getLogger("eea.climateadapt.arcgis")

REFERER = 'climate-adapt.europa.eu CaseStudies Sync'


def _get_token_service_url(endpoint):
    """ Interogate the endpoint to find out URL for authentication tokens """

    url = endpoint + "/info?f=pjson"
    j = requests.get(url).json()

    return j['authInfo']['tokenServicesUrl']


def get_auth_token(settings=None):
    """ Retrieves an authentication token
    """

    if settings is None:
        settings = get_settings()
    endpoint = get_endpoint_url(settings)
    token_url = _get_token_service_url(endpoint)
    data = {
        'f': 'json',
        'username': settings.username,
        'password': settings.password,
        'referer': REFERER,
    }
    resp = requests.post(token_url, data=data)
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
    layer_url = get_feature_url()
    data = {
        'f': 'json',
        'useGlobalIds': True,
        'where': filter,
        # 'outFields': 'objectid,itemname,measureid,FID,globalid', #"*"
        'outFields': '*',
        'token': token,
        'referer': REFERER
    }
    url = "{0}/query".format(layer_url)
    resp = requests.get(url, params=data)

    return resp.json()


def apply_edits(data, op='updates', token=None):
    """ Makes a applyEdits request to arcgis

    See http://resources.arcgis.com/en/help/arcgis-rest-api/ for help
    """

    settings = get_settings()

    if token is None:
        token = get_auth_token(settings)

    layer_url = get_feature_url(settings)

    data = {
        'f': 'json',
        'token': token,
        'referer': REFERER,
        op: data,
    }
    url = "{0}/applyEdits".format(layer_url)
    resp = requests.post(url, data=data)
    res = resp.json()

    return res


def _get_obj_OBJECTID(obj=None, uid=None, token=None):
    """ The "Object ID Field" for the casestudies_pointLayer is "OBJECTID".

    Because the casestudies_pointLayer doesn't use Global Ids, we need to
    identify objects by their OBJECTID.
    """

    if token is None:
        token = get_auth_token()

    if obj is not None:
        measureid = _measure_id(obj)
    else:
        measureid = uid

    res = query_layer(filter='measureid={0}'.format(measureid), token=token)

    if len(res['features']) == 0:
        return None

    # fid = res['features'][0]['attributes']['FID']
    fid = res['features'][0]['attributes']['OBJECTID']
    logger.info("Got OBJECTID %s for measureid %s", fid, measureid)

    return fid
