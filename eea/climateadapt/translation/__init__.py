"""Init"""

import json
import logging
import os
from datetime import datetime

import base64
import chardet
import requests
from requests.auth import HTTPDigestAuth

import transaction
from BTrees.OOBTree import OOBTree
from langdetect import detect
from persistent import Persistent
from plone.api import portal

from .interfaces import ITranslationsStorage

from zeep import Client
from zeep.wsse.username import UsernameToken

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


# Detect the source language for countries which have more official languages
TRANS_LANGUAGE_MAPPING = {
    # 'DE': lambda text: 'DE'
    "BE": get_detected_lang,
    "SE": get_detected_lang,
}

# For the following countries, the translation service uses
# different country code
ALTERNATE_COUNTRY_CODES = {
    "SI": "SL",
}


def get_mapped_language(country_code, text):
    detect_func = TRANS_LANGUAGE_MAPPING[country_code]
    detected_lang = detect_func(text)

    if not detected_lang:
        return country_code

    if detected_lang == "en":
        return country_code

    return detected_lang.upper()


def _get_country_code(country_code, text):
    if country_code in TRANS_LANGUAGE_MAPPING:
        country_code = get_mapped_language(country_code, text)

    if country_code in ALTERNATE_COUNTRY_CODES:
        country_code = ALTERNATE_COUNTRY_CODES.get(country_code, country_code)

    return country_code


def decode_text(text):
    encoding = chardet.detect(text)["encoding"]
    text_encoded = text.decode(encoding)

    # import unicodedata
    # text_encoded = unicodedata.normalize('NFKD', text_encoded)

    return text_encoded


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


def retrieve_html_translation(source_lang, html, obj_path, target_languages=None):
    """Send a call to automatic translation service, to translate a string
    Returns a json formatted string
    """
    if not html:
        return

    if not target_languages:
        target_languages = ["EN"]

    encoded_html = base64.b64encode(html)

    site_url = portal.get().absolute_url()

    if "localhost" in site_url:
        logger.warning(
            "Using localhost, won't retrieve translation for: %s", html)

    client = Client(
        "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL",
        wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
    )

    dest = "{}/@@translate-callback?source_lang={}&format=html".format(
        site_url, source_lang
    )

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


def translate_one_text_to_translation_storage(
    country_code, text, target_languages=None, force=False
):
    """Send a call to automatic translation service, to translate a string
    Returns a json formatted string
    """

    country_code = _get_country_code(country_code, text)

    if not text:
        return {}

    if not target_languages:
        target_languages = ["EN"]

    translation = get_translated(text, target_languages[0])

    if translation:
        if not (force == "True" or ("...." in translation)):
            # don't translate already translated strings, it overrides the
            # translation
            res = {"transId": translation,
                   "externalRefId": text, "translated": True}
            logger.info("Data translation cached : %r", res)
            return res

    site_url = portal.get().absolute_url()

    if "localhost" in site_url:
        logger.warning(
            "Using localhost, won't retrieve translation for: %s", text)

        # return {}

    # if detected language is english skip translation

    # if get_detected_lang(text) == 'en':
    #     logger.info(
    #         "English language detected, won't retrive translation for: %s",
    #         text
    #     )
    #
    #     return

    dest = "{}/@@translate-callback?source_lang={}".format(
        site_url, country_code)

    # logger.info('Translate callback URL: %s', dest)

    data = {
        "priority": 5,
        "callerInformation": {
            "application": "Marine_EEA_20180706",
            "username": TRANS_USERNAME,
        },
        "domain": "SPD",
        "externalReference": text,  # externalReference,
        "textToTranslate": text,
        "sourceLanguage": country_code,
        "targetLanguages": target_languages,
        "destinations": {
            "httpDestinations": [dest],
        },
    }

    logger.info("Data translation request : %r", data)

    resp = requests.post(
        SERVICE_URL,
        auth=HTTPDigestAuth("Marine_EEA_20180706", MARINE_PASS),
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    logger.info("Response from translation request: %r", resp.content)

    res = {"transId": resp.content, "externalRefId": text}

    return res


def translate_one_field_in_one_step(
    country_code,
    text,
    target_languages=None,
    uid=None,
    obj_path=None,
    field=None,
    tile_data=None,
    tile_id=None,
):
    """Translate simple text fields in one step.

    Send a call to automatic translation service, to translate a string
    Returns a json formatted string

    The result will be automatically saved to specified obj and field
    on callback, without using annotations.
    """

    if not text:
        return

    country_code = _get_country_code(country_code, text)
    site_url = portal.get().absolute_url()

    dest = ""

    is_cover = False
    if tile_data is not None:
        dest = "{}/@@translate-callback?one_step=true&source_lang={}&uid={}&field={}&is_cover=true&tile_id={}".format(
            site_url, country_code, uid, field, tile_id
        )
        is_cover = True

    if not target_languages:
        target_languages = ["EN"]

    if "localhost" in site_url:
        logger.warning(
            "Using localhost, won't retrieve translation for: %s", text)

    if is_cover is False:
        dest = "{}/@@translate-callback?one_step=true&source_lang={}&uid={}&field={}".format(
            site_url, country_code, uid, field
        )
    data = {
        "priority": 5,
        "callerInformation": {
            "application": "Marine_EEA_20180706",
            "username": TRANS_USERNAME,
        },
        "domain": "SPD",
        "externalReference": obj_path,
        "textToTranslate": text,
        "sourceLanguage": country_code,
        "targetLanguages": target_languages,
        "destinations": {
            "httpDestinations": [dest],
        },
    }

    logger.info("One step translation request : %r", data)

    resp = requests.post(
        SERVICE_URL,
        auth=HTTPDigestAuth("Marine_EEA_20180706", MARINE_PASS),
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
    )
    logger.info("One step: resp from translation request: %r", resp.content)

    res = {"transId": resp.content, "externalRefId": text}

    return res


def get_translation_keys(site=None):
    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)

    return list(storage.keys())


def get_translation_report(site=None):
    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)
    report = {"nr_keys": len(storage.keys()), "items": {}}
    data = storage.keys()
    for i in range(len(data)):
        storage_key = storage.get(data[i])
        languages = set(storage_key.keys())
        for language in languages:
            if language not in report["items"]:
                report["items"][language] = 0
            report["items"][language] += 1

    return report


def get_translation_key_values(key, site=None):
    if site is None:
        site = portal.get()

    res = []
    storage = ITranslationsStorage(site)
    storage_key = storage.get(key, None)
    if storage_key:
        languages = set(storage_key.keys())
        for language in languages:
            res.append(
                {"language": language,
                    "translation": storage_key.get(language, None)}
            )
    return res


def get_translated(value, language, site=None):
    language = _get_country_code(language, value)

    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)

    translated = storage.get(value, {}).get(language, None)

    if translated:
        if hasattr(translated, "text"):
            return translated.text.lstrip("?")

        return translated.lstrip("?")


def normalize(text):
    if not isinstance(text, basestring):
        return text

    if isinstance(text, str):
        text = text.decode("utf-8")

    if not text:
        return text

    text = text.strip().replace("\r\n", "\n").replace("\r", "\n")

    return text


def delete_translation(text, source_lang):
    source_lang = _get_country_code(source_lang, text)

    site = portal.get()

    storage = ITranslationsStorage(site)

    if storage.get(source_lang, None):
        decoded = normalize(text)

        if text in storage[source_lang]:
            del storage[source_lang][text]

        if decoded in storage[source_lang]:
            del storage[source_lang][decoded]

            # I don't think this is needed
            storage[source_lang]._p_changed = True
            transaction.commit()


def save_translation(original, translated, source_lang, target_lang, approved=False):
    source_lang = _get_country_code(source_lang, original)

    logger.info(
        "Translate callback save: %s :: %s :: %s :: %s",
        original,
        translated,
        source_lang,
        target_lang,
    )
    site = portal.get()

    storage = ITranslationsStorage(site)

    storage_original = storage.get(original, None)

    if storage_original is None:
        storage_original = OOBTree()
        storage[original] = storage_original

    translated = Translation(translated)
    storage_original[target_lang] = translated

    logger.info("Saving to annotation: %s", translated)
