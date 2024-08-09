"""Init"""

import base64
import logging
import os
from datetime import datetime

from langdetect import detect
from persistent import Persistent
from plone.api import portal
from zeep import Client
from zeep.wsse.username import UsernameToken

# from .interfaces import ITranslationsStorage
# from BTrees.OOBTree import OOBTree

env = os.environ.get

ANNOTATION_KEY = "translation.cca.storage"
TRANS_USERNAME = "ipetchesi"  # TODO: get another username?
MARINE_PASS = env("MARINE_PASS", "")
SERVICE_URL = "https://webgate.ec.europa.eu/etranslation/si/translate"

logger = logging.getLogger("wise.msfd.translation")


def get_detected_lang(text):
    """Detect the language of the text, return None for short texts"""

    if len(text) < 50:
        return None

    try:
        detect_lang = detect(text)
    except:
        # Can't detect language if text is an url
        # it throws LangDetectException
        return None

    return detect_lang


class Translation(Persistent):
    def __init__(self, text, source=None):
        self.text = text
        self.source = source
        self.approved = False
        self.modified = datetime.now()

    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text


def retrieve_volto_html_translation(
    http_host, source_lang, html, obj_path, target_languages=None
):
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
        logger.warning(
            "Using localhost, won't retrieve translation for: %s", html)

    client = Client(
        "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL",
        wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
    )

    dest = "{}/@@translate-callback?source_lang={}&format=html&is_volto=1".format(
        http_host, source_lang
    )
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

    res = {"transId": resp, "externalRefId": html}

    return res


def normalize(text):
    if not isinstance(text, basestring):
        return text

    if isinstance(text, str):
        text = text.decode("utf-8")

    if not text:
        return text

    text = text.strip().replace("\r\n", "\n").replace("\r", "\n")

    return text
