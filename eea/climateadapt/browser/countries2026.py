import csv
import json
import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from datetime import datetime
from plone.api import portal
from Products.Five.browser import BrowserView

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import ace_countries


def get_country_code(country_name):
    if "Moldova" == country_name:
        country_name = "Moldova, Republic of"
    if "Moldavia" == country_name:
        country_name = "Moldova, Republic of"
    country_code = next((k for k, v in ace_countries if v == country_name), "Not found")
    if country_code == "GR":
        country_code = "EL"
    if country_code == "Not found" and country_name.lower() == "turkiye":
        country_code = "TR"

    return country_code


def setup_discodata(annotations, is_energy_comunity=False):
    call_discodata_url = (
        DISCODATA_ENERGY_COMUNITY_URL if is_energy_comunity else DISCODATA_URL
    )
    response = urllib.request.urlopen(call_discodata_url)
    data = json.loads(response.read())
    annotations_discodata_key = "discodata_country_2025"
    if is_energy_comunity:
        annotations_discodata_key += "_energy_comunity"
    annotations[annotations_discodata_key] = {"timestamp": datetime.now(), "data": data}
    annotations._p_changed = True
    logger.info("RELOAD URL %s", call_discodata_url)

    return data


def get_discodata(is_energy_comunity=False):
    annotations = portal.getSite().__annotations__

    annotations_discodata_key = "discodata_country_2025"
    if is_energy_comunity:
        annotations_discodata_key += "_energy_comunity"

    if annotations_discodata_key not in annotations:
        annotations._p_changed = True
        return setup_discodata(annotations, is_energy_comunity)

    last_import_date = annotations[annotations_discodata_key]["timestamp"]

    if (datetime.now() - last_import_date).total_seconds() > 60**2:
        # if (datetime.now() - last_import_date).total_seconds() > 0:
        # if (datetime.now() - last_import_date).total_seconds() > 60:
        annotations._p_changed = True
        return setup_discodata(annotations, is_energy_comunity)

    return annotations[annotations_discodata_key]["data"]


def get_discodata_for_country(country_code):
    data = get_discodata(country_code.upper() in ["GE", "MD", "RS", "UA"])

    orig_data = next(
        (x for x in data["results"] if x["countryCode"] == country_code), {}
    )

    # import pdb; pdb.set_trace()
    # remove the countryCode as we don't need it
    processed_data = {
        k: str(v)
        for k, v in list(orig_data.items())
        if k not in ["countryCode", "ReportNet3HistoricReleaseId"]
    }

    # some values are strings, and need to be transformed
    # import pdb; pdb.set_trace()
    # into Python objects
    for k, val in list(processed_data.items()):
        try:
            if val == "None":
                processed_data[k] = None
                continue
            json_val = json.loads(val)
            new_value = None

            if isinstance(json_val, dict):
                new_value = json_val[k][0] if 1 == len(json_val[k]) else json_val[k]

                processed_data[k] = new_value
            # else:
            #    processed_data[k] = None
        except:
            logger.info("EMPTY DATA 114 : %s", k)

    return processed_data


# DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_JSON%5D&p=1&nrOfHits=100'
# DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2023%5D&p=1&nrOfHits=100"
DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=Select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2025%5D&p=1&nrOfHits=50&mail=null&schema=null"
DISCODATA_ENERGY_COMUNITY_URL = "https://discodata.eea.europa.eu/sql?query=Select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BEC_Adaptation_Art19_JSON_2025%5D&p=1&nrOfHits=50&mail=null&schema=null"
logger = logging.getLogger("eea.climateadapt")


class CountryProfileJson(BrowserView):
    def __call__(self):
        response = self.request.response
        response.setHeader("Content-Type", "application/json")
        response.setStatus(200)

        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        return json.dumps(processed_data)

    def verify_country_name(self, country_name):
        if country_name.lower in ["turkiye"]:
            country_name = "Turkey"
        return country_name

    def get_country_code(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        return get_country_code(country_name)
