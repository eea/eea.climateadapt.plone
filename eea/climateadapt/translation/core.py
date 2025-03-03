import base64
import json
import logging
import os

import redis
import requests
from Acquisition import aq_inner, aq_parent
from plone import api
from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zeep import Client
from zeep.wsse.username import UsernameToken
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from eea.climateadapt.callbackdatamanager import queue_callback
from eea.climateadapt.utils import force_unlock
from eea.climateadapt.versions import ISerialId

from .constants import LANGUAGE_INDEPENDENT_FIELDS

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
            data = dict(data.items(), language=language)

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


def get_content_from_html(html, language=None):
    """Given an HTML string, converts it to Plone content data"""

    data = {"html": html, "language": language}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(CONTENT_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    data = req.json()["data"]
    logger.info("Data from converter: %s", data)

    # because the blocks deserializer returns {blocks, blocks_layout} and is saved in "blocks", we need to fix it
    if data.get("blocks"):
        blockdata = data["blocks"]
        data["blocks_layout"] = blockdata["blocks_layout"]
        data["blocks"] = blockdata["blocks"]

    logger.info("Data with tiles decrypted %s", data)

    return data


def save_field_data(canonical, trans_obj, fielddata):
    """Applies the data from fielddata to the translated object trans_obj"""

    for schema in iterSchemata(canonical):
        for k, v in getFieldsInOrder(schema):
            if (
                ILanguageIndependentField.providedBy(v)
                or k in LANGUAGE_INDEPENDENT_FIELDS
                or k not in fielddata
            ):
                continue

            value = fielddata[k]

            if IRichText.providedBy(v):
                value = RichTextValue(value)

            setattr(trans_obj, k, value)


def copy_missing_interfaces(en_obj, trans_obj):
    """Make sure all interfaces are copied from english obj to translated obj"""
    en_i = [(x.getName(), x) for x in en_obj.__provides__.interfaces()]
    trans_i = [(x.getName(), x) for x in trans_obj.__provides__.interfaces()]
    missing_i = [x for x in en_i if x not in trans_i]
    if len(missing_i) > 0:
        logger.info("Missing interfaces: %s" % len(missing_i))
        for interf in missing_i:
            alsoProvides(trans_obj, interf[1])
            trans_obj.reindexObject()
            logger.info("Copied interface: %s" % interf[0])


def handle_link(en_obj, trans_obj):
    link = getattr(en_obj, "remoteUrl", None)
    logger.info("Fixing link %s (%s)", trans_obj.absolute_url(), link)
    if link:
        link = link.replace("/en/", "/%s/" % trans_obj.language)
        logger.info("Fixed with: %s", link)
        trans_obj.remoteUrl = link
    trans_obj._p_changed = True


def sync_translation_state(trans_obj, en_obj):
    state = None
    transitions = {
        "published": "publish",
        "archived": "archive",
    }

    try:
        state = api.content.get_state(en_obj)
    except WorkflowException:
        logger.error("Can't get state for original object: %s", en_obj)
        pass

    if state in ["published", "archived"]:
        if api.content.get_state(trans_obj) != state:
            wftool = getToolByName(trans_obj, "portal_workflow")
            logger.info("%s %s", state, trans_obj.absolute_url())
            if state in transitions:
                try:
                    wftool.doActionFor(trans_obj, transitions[state])
                except WorkflowException:
                    logger.warning("Could not sync state for: %s", trans_obj)

    if en_obj.EffectiveDate() != trans_obj.EffectiveDate():
        trans_obj.setEffectiveDate(en_obj.effective_date)
        trans_obj._p_changed = True

    if en_obj.__ac_local_roles__ != trans_obj.__ac_local_roles__:
        trans_obj._p_changed = True
        trans_obj.__ac_local_roles__ = en_obj.__ac_local_roles__


def ingest_html(trans_obj, html):
    """Used by the translation callback"""

    force_unlock(trans_obj)
    fielddata = get_content_from_html(html, language=trans_obj.language)

    translations = TranslationManager(trans_obj).get_translations()

    if "en" not in translations:
        path = "/".join(trans_obj.getPhysicalPath())
        msg = (
            "Could not find canonical for this object %s, aborting. "
            "Check its translation group" % path
        )

        logger.warning(msg)
        raise ValueError(msg)

    en_obj = translations["en"]  # hardcoded, should use canonical

    save_field_data(en_obj, trans_obj, fielddata)

    copy_missing_interfaces(en_obj, trans_obj)

    # if trans_obj.portal_type in ("Folder", "Document"):
    #     handle_folder_doc_step_4(en_obj, trans_obj, False, False)
    if trans_obj.portal_type in ["Link"]:
        handle_link(en_obj, trans_obj)

    # TODO: sync workflow state
    sync_translation_state(trans_obj, en_obj)

    trans_obj._p_changed = True
    trans_obj.reindexObject()


def check_ancestors_path_exists(obj, language, site_portal):
    """Create full path for a object"""

    parent = aq_parent(aq_inner(obj))

    if parent is None:
        return True

    path = parent.getPhysicalPath()

    if len(path) <= 2:  # aborting, we've reached bottom
        return True

    translations = TranslationManager(parent).get_translations()
    if language not in translations:
        # TODO, what if the parent path already exist in language
        # but is not linked in translation manager
        setup_translation_object(parent, language, site_portal)


def safe_traverse(obj, trans_path):
    parts = trans_path.strip("/").split("/")
    current_obj = obj

    for part in parts:
        if hasattr(current_obj, "objectIds") and callable(current_obj.objectIds):
            if part in current_obj.objectIds():
                current_obj = current_obj[part]
            else:
                return None
        # elif hasattr(current_obj, part):
        #     current_obj = getattr(current_obj, part)
        else:
            return None

    return current_obj


def setup_translation_object(obj, language, site_portal):
    """Create translation object for an obj"""

    # rc = RequestContainer(REQUEST=obj.REQUEST)
    tm = TranslationManager(obj)
    translations = tm.get_translations()

    if language in translations:
        logger.info("Skip creating translation. Already exists.")
        translated_object = translations[language]

        copy_missing_interfaces(obj, translated_object)
        sync_translation_state(translated_object, obj)
        translated_object.reindexObject()

        return translated_object

    path = obj.getPhysicalPath()
    trans_path = []
    for bit in path:
        if bit == "en":
            bit = language
        trans_path.append(bit)
    trans_path = "/".join(trans_path)

    trans = None
    try:
        trans = safe_traverse(obj, trans_path)
    except Exception:
        pass

    if trans is not None:
        # todo: fix the trans
        logger.warning(
            "Translation object exists, but it's not properly recorded %s %s %s",
            "/".join(trans.getPhysicalPath()),
            "/".join(obj.getPhysicalPath()),
            # trans_path,
        )
        trans.reindexObject()

        return trans

    check_ancestors_path_exists(obj, language, site_portal)
    factory = DefaultTranslationFactory(obj)

    translated_object = factory(language)

    tm.register_translation(language, translated_object)

    # https://github.com/plone/plone.app.multilingual/blob/2.x/src/plone/app/multilingual/manager.py#L85
    # translated_object.reindexObject()   ^ already reindexed.

    # In cases like: /en/page-en -> /fr/page, fix the url: /fr/page-en
    try:
        if translated_object.id != obj.id:
            translated_object.aq_parent.manage_renameObject(
                translated_object.id, obj.id
            )
    except Exception:
        logger.info("CREATE ITEM: cannot rename the item id - already exists.")

    copy_missing_interfaces(obj, translated_object)
    sync_translation_state(translated_object, obj)

    translated_object.reindexObject()

    return translated_object
