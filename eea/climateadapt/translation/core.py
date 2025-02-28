import base64
import json
import logging
import os

import redis
import requests
from plone.api import portal
from zeep import Client
from zeep.wsse.username import UsernameToken
from zope.component import getMultiAdapter

from eea.climateadapt.callbackdatamanager import queue_callback
from eea.climateadapt.versions import ISerialId

env = os.environ.get

TRANS_USERNAME = "ipetchesi"  # TODO: get another username?
MARINE_PASS = env("MARINE_PASS", "")
SERVICE_URL = "https://webgate.ec.europa.eu/etranslation/si/translate"
ETRANSLATION_SOAP_SERVICE_URL = (
    "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL"
)

# See this for schema:
# https://webgate.ec.europa.eu/etranslation/si/SecuredWSEndpointHandlerService?xsd=1

logger = logging.getLogger("eea.climateadapt")

SLATE_CONVERTER = "http://converter:8000/html"
BLOCKS_CONVERTER = "http://converter:8000/blocks2html"
CONTENT_CONVERTER = "http://converter:8000/html2content"

logger = logging.getLogger("eea.climateadapt")


def queue_job(queue_name, job_name, data, opts=None):
    """Schedules job for redis, at the end of the transaction"""

    opts = opts or {
        "delay": 0,  # Delay in milliseconds
        "priority": 1,
        "attempts": 3,
    }

    job_data = {
        "name": job_name,
        "data": data,
        "opts": opts,
    }

    r = redis.Redis(host="localhost", port=6379, db=0)
    data = json.dumps(job_data)

    def callback():
        r.lpush(queue_name, data)

    queue_callback(callback)

    print(f"Job added to queue: {queue_name}")


def queue_translate_volto_html(obj, language=None):
    """The "new" method of triggering the translation of an object.

    While this is named "volto", it is a generic system to translate Plone
    content. The actual "ingestion" of translated data is performed in the
    TranslationCallback view

    Input: html (generated from volto blocks and obj fields, as string)
           en_obj - the object to be translated
           http_host - website url

    Makes sure translation objects exists and requests a translation for
    all languages.
    """
    html = getMultiAdapter((obj, obj.REQUEST), name="tohtml")()
    url = obj.absolute_url()
    serial_id = ISerialId(obj)

    data = {"obj_url": url, "html_content": html, "serial_id": serial_id}

    logger.info("Called translate_volto_html for %s", url)
    languages = language and [language] or []  # get_site_languages()

    if "cca/en" in url:
        for language in languages:  # temporary
            if language == "en":
                continue

            queue_job("etranslation", "call_etranslation", data)


def get_blocks_as_html(obj):
    """Uses the external converter service to convert the blocks to HTML representation"""

    data = {"blocks_layout": obj.blocks_layout, "blocks": obj.blocks}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(BLOCKS_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    html = req.json()["html"]
    logger.info("Blocks converted to html: %s", html)
    return html


def call_etranslation_service(source_lang, html, obj_path, target_languages=None):
    """Makes a eTranslation webcall to request a translation for a html
    (based on volto export)
    """

    if not html:
        return

    if not target_languages:
        target_languages = ["EN"]

    encoded_html = base64.b64encode(html)

    site_url = portal.get().absolute_url()  # -> '/cca'

    if "localhost" in site_url:
        logger.warning("Is localhost, won't retrieve translation for: %s", html)
        return

    client = Client(
        ETRANSLATION_SOAP_SERVICE_URL,
        wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
    )

    dest = "{}/@@translate-callback?source_lang={}".format(site_url, source_lang)
    if "https://" not in dest:
        dest = "https://" + dest

    resp = client.service.translate(
        {
            "priority": "5",
            "external-reference": obj_path,
            "caller-information": {
                "application": "Marine_EEA_20180706",
                "username": TRANS_USERNAME,
            },
            "document-to-translate-base64": {
                "content": encoded_html,
                "format": "html",
                "fileName": "out",
            },
            "source-language": source_lang,
            "target-languages": {"target-language": target_languages},
            "domain": "GEN",
            "output-format": "html",
            "destinations": {
                "http-destination": dest,
            },
        }
    )

    logger.info("Data translation request : html content")
    logger.info("Response from translation request: %r", resp)

    # if str(resp[0]) == '-':
    #     # If the response is a negative number this means error. Error codes:
    #     # https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/How+to+submit+a+translation+request+via+the+CEF+eTranslation+webservice
    #     import pdb; pdb.set_trace()

    return {"transId": resp, "externalRefId": html}
