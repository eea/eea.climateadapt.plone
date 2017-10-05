""" Debugging code, historical code
"""

import json
import logging
import os

import requests

logger = logging.getLogger('eea.climateadapt.arcgis')


USERNAME = "eea_casestudies"
PASSWORD = os.environ.get('GISPASS', "")

SERVER_NAME = "LcQjj2sL7Txk9Lag"
ENDPOINT = "http://services.arcgis.com/{0}/ArcGIS/rest".format(SERVER_NAME)
FEATURE = "casestudies_pointLayer_clone"
LAYER_URL = "{0}/services/{1}/FeatureServer/0".format(ENDPOINT, FEATURE)

REFERER = 'climate-adapt.europa.eu CaseStudies Sync'


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
