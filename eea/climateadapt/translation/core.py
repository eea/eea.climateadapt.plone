import asyncio
import base64
import json
import logging
import os

import requests
from Acquisition import aq_inner, aq_parent
from bullmq import Queue
from plone import api
from plone.api import content, portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.interfaces import ITranslationManager, ITG, IMutableTG
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zeep import Client
from zeep.wsse.username import UsernameToken
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from eea.climateadapt.callbackdatamanager import queue_callback
from eea.climateadapt.utils import force_unlock
from eea.climateadapt.versions import ISerialId

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .utils import get_site_languages

env = os.environ.get

TRANS_USERNAME = "ipetchesi"  # TODO: get another username?
MARINE_PASS = env("MARINE_PASS", "")
SERVICE_URL = "https://webgate.ec.europa.eu/etranslation/si/translate"
ETRANSLATION_SOAP_SERVICE_URL = (
    "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL"
)
REDIS_HOST = env("REDIS_HOST", "localhost")
REDIS_PORT = int(env("REDIS_PORT", 6379))
TRANSLATION_AUTH_TOKEN = env("TRANSLATION_AUTH_TOKEN", "")
PORTAL_URL = os.environ.get("PORTAL_URL", "")

# See this for schema:
# https://webgate.ec.europa.eu/etranslation/si/SecuredWSEndpointHandlerService?xsd=1

logger = logging.getLogger("eea.climateadapt")

CONVERTER_URL = env("CONVERTER_URL", "http://converter:8000")
SLATE_CONVERTER = f"{CONVERTER_URL}/html"
BLOCKS_CONVERTER = f"{CONVERTER_URL}/blocks2html"
CONTENT_CONVERTER = f"{CONVERTER_URL}/html2content"

logger = logging.getLogger("eea.climateadapt")

redisOpts = dict(host=REDIS_HOST, port=REDIS_PORT, db=0)

queues = {
    "etranslation": lambda: Queue("etranslation", {"connection": redisOpts}),
    "save_etranslation": lambda: Queue("save_etranslation", {"connection": redisOpts}),
    "sync_paths": lambda: Queue("sync_paths", {"connection": redisOpts}),
}


def queue_job(queue_name, job_name, data, opts=None):
    """Schedules job for redis, at the end of the transaction"""

    opts = opts or {
        "delay": 1000,  # Delay in milliseconds
        "priority": 10,
        "attempts": 1,
        "lifo": False,  # we dont use LIFO queing
    }

    def callback():
        logger.info("Adding job %s", job_name)

        async def inner():
            queue = queues[queue_name]()
            await queue.add(job_name, data, opts)
            await queue.close()

        asyncio.run(inner())

    queue_callback(callback)

    print(f"Job added to queue: {queue_name}")


def queue_translate(obj, language=None):
    """Triggering the translation of an object."""

    url = "/".join(obj.getPhysicalPath()[1:])
    try:
        html = getMultiAdapter((obj, obj.REQUEST), name="tohtml")()
    except Exception:
        logger.exception("Could not convert Volto page to HTML: %s", url)
        return

    serial_id = int(ISerialId(obj))  # by default we get is a location proxy

    data = {"obj_url": url, "html": html, "serial_id": serial_id}

    languages = language and [language] or get_site_languages()
    logger.info("Called translate_volto_html for %s", url)

    # Schedule the job to be executed between 7 PM and 7 AM
    import datetime
    now = datetime.datetime.now()
    # 19:00 = 7 PM, 07:00 = 7 AM
    start_time_limit = now.replace(hour=19, minute=0, second=0, microsecond=0)
    end_time_limit = now.replace(hour=7, minute=0, second=0, microsecond=0)
    
    delay = 1000 # default delay

    if 7 <= now.hour < 19:
        # We are during the day (forbidden window). Schedule for 7 PM tonight.
        wait_time = start_time_limit - now
        delay = int(wait_time.total_seconds() * 1000)
        logger.info("Delaying translation job for %s seconds", wait_time.total_seconds())

    for language in languages:
        if language == "en":
            continue

        data = dict(data.items(), language=language)
        
        opts = {"delay": delay}

        logger.info("Queue translate_volto_html for %s / %s", url, language)
        queue_job("etranslation", "call_etranslation", data, opts)


def get_blocks_as_html(obj):
    """Uses the converter service to convert blocks to HTML representation"""

    data = {"blocks_layout": obj.blocks_layout, "blocks": obj.blocks}
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    req = requests.post(BLOCKS_CONVERTER, data=json.dumps(data), headers=headers)
    if req.status_code != 200:
        logger.debug(req.text)
        raise ValueError

    html = req.json()["html"]
    logger.info("Blocks converted to html: %s", html)
    return html


def call_etranslation_service(html, obj_path, target_languages):
    """Makes a eTranslation webcall to request a translation for a html
    (based on volto export)
    """

    if not html:
        return

    encoded_html = base64.b64encode(html.encode("utf-8"))

    site_url = PORTAL_URL or portal.get().absolute_url()

    client = Client(
        ETRANSLATION_SOAP_SERVICE_URL,
        wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
    )

    dest = "{}/@@translate-callback".format(site_url)

    if "localhost" not in site_url:
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
                "source-language": "en",
                "target-languages": {"target-language": target_languages},
                "domain": "GEN",
                "output-format": "html",
                "destinations": {
                    "http-destination": dest,
                },
            }
        )
    else:
        logger.warning("Is localhost, won't retrieve translation for: %s", html)
        return {"transId": "not-called", "externalRefId": html}

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

    # because the blocks deserializer returns {blocks, blocks_layout} and is
    # saved in "blocks", we need to fix it
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
    """Make sure all interfaces are copied from en obj to translated obj"""
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
        logger.debug("Can't get state for original object: %s", en_obj)
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

    trans_tm = ITranslationManager(trans_obj)
    translations = trans_tm.get_translations()

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


def check_ancestors_path_exists(obj, language, request):
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
        setup_translation_object(parent, language, request)
        queue_translate(parent, language)


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


def get_translated_path(canonical, language):
    path = canonical.getPhysicalPath()
    trans_path = []
    for bit in path:
        if bit == "en":
            bit = language
        trans_path.append(bit)
    trans_path = "/".join(trans_path)
    return trans_path


def unsafe_register_translation(language, tg, obj):
    """register a translation for an existing content"""

    if not language and language != "":
        raise KeyError("There is no target language")

    catalog = portal.get_tool("portal_catalog")

    brains = catalog.unrestrictedSearchResults(TranslationGroup=tg, Language=language)
    for brain in brains:
        o = brain.getObject()
        logger.warning(f"Deleting trans at wrong path: {o.absolute_url()}")
        content.delete(obj=o, check_linkintegrity=False)

    # register the new translation in the canonical
    IMutableTG(obj).set(tg)
    obj.reindexObject(idxs=("Language", "TranslationGroup"))


def setup_translation_object(canonical, language, request):
    """Create translation object for an obj"""

    site = portal.get()

    # rc = RequestContainer(REQUEST=obj.REQUEST)
    tm = ITranslationManager(canonical)
    tg = ITG(canonical)
    translations = tm.get_translations()

    if language in translations:
        logger.info("Skip creating translation. Already exists.")
        translated_object = translations[language]

        trans_path = "/".join(translated_object.getPhysicalPath())
        if trans_path == get_translated_path(canonical, language):
            copy_missing_interfaces(canonical, translated_object)
            sync_translation_state(translated_object, canonical)
            translated_object.reindexObject()

            return translated_object
        else:
            logger.info(
                f"Removing translation {trans_path} because it's different path"
            )
            content.delete(obj=translated_object, check_linkintegrity=False)

    trans_path = get_translated_path(canonical, language)

    trans = None
    try:
        trans = safe_traverse(site, trans_path)
    except Exception:
        pass

    if trans is not None:
        # todo: fix the trans
        logger.warning(
            "Translation object exists, but it's not properly recorded %s %s %s. It will be re-registed with the proper translation group",
            "/".join(trans.getPhysicalPath()),
            "/".join(canonical.getPhysicalPath()),
            # trans_path,
        )
        # TODO: make sure objects are compatible
        tg_id = ITG(canonical)
        unsafe_register_translation(language, tg_id, trans)

        return trans

    check_ancestors_path_exists(canonical, language, request)

    factory = DefaultTranslationFactory(canonical)

    request.translation_info = {"tg": tg, "source_language": "en"}
    translated_object = factory(language)

    assert translated_object is not None

    tm.register_translation(language, translated_object)

    # In cases like: /en/page-en -> /fr/page, fix the url: /fr/page-en
    try:
        if translated_object.id != canonical.id:
            translated_object.aq_parent.manage_renameObject(
                translated_object.id, canonical.id
            )
    except Exception:
        logger.info("CREATE ITEM: cannot rename the item id - already exists.")
        raise

    copy_missing_interfaces(canonical, translated_object)
    sync_translation_state(translated_object, canonical)

    translated_object.reindexObject()

    return translated_object


def check_token_security(request):
    token = request.getHeader("Authentication")
    if token != TRANSLATION_AUTH_TOKEN:
        raise Unauthorized


def find_untranslated(obj, good_lang_codes):
    tm = ITranslationManager(obj)
    translations = tm.get_translations()
    untranslated = set(good_lang_codes)
    base_path = obj.getPhysicalPath()[1:]

    for langcode, trans in translations.items():
        if langcode == "en":
            continue

        if trans.title and langcode in untranslated:
            untranslated.remove(langcode)

        if trans.getPhysicalPath()[1:] != base_path:
            logger.warn(
                "Unmatched physical paths %s - %s / %s - %s",
                obj.absolute_url(),
                trans.absolute_url(),
                trans.getPhysicalPath()[1:],
                base_path,
            )

    return list(untranslated)


def sync_translation_paths(
    oldParent, oldName, newParent, newName, langs=None, request=None
):
    result = {}
    en_path = f"{oldParent}/{oldName}"
    en_obj = content.get(en_path)

    if en_obj is None:
        msg = f"Could not find original source for move: {en_path}"
        logger.warning(msg)
        return {"status": msg}

    try:
        tm = ITranslationManager(en_obj)
    except TypeError:
        logger.error("Could not find ITranslationManager for %s", en_obj.absolute_url())
        raise

    translations = tm.get_translations()

    for lang, trans_obj in translations.items():
        if lang == "en":
            continue

        if langs and lang not in langs:
            continue

        if len(en_obj.aq_parent.getPhysicalPath()) > 3:
            setup_translation_object(en_obj.aq_parent, lang, request)

        old_path = "/".join(trans_obj.getPhysicalPath())

        if "/en/" in newParent:
            new_parent = newParent.replace("/en/", f"/{lang}/")
        elif newParent.endswith("/en"):
            new_parent = newParent.replace("/en", f"/{lang}")
        else:
            logger.warning("Could not find destination parent to move: %s", newParent)
            raise ValueError("Could not find destination parent to move: %s", newParent)

        target = content.get(new_parent)

        if target is None:
            logger.warning("Could not find target to be moved: %s", new_parent)
            # TODO: create it with setup_translation_object() ?
            raise ValueError("Could not find target to be moved: %s", new_parent)

        target_obj_path = "/".join(target.getPhysicalPath()) + "/" + newName
        existing_trans = content.get(target_obj_path)
        test_path = ["", "cca", "en", "mission"]
        if existing_trans is not None:
            if len(target.getPhysicalPath()) < len(test_path):
                raise ValueError(
                    "Need to delete this object, but it's too big %s", target_obj_path
                )

            # brains = en_obj.portal_catalog.searchResults(
            #     path=target_obj_path,
            #     sort="path",
            # )

            logger.info(
                "This translation object already exists %s, removing", target_obj_path
            )
            content.delete(existing_trans, check_linkintegrity=False)

        # TODO: setup_translation_object()
        try:
            moved = content.move(source=trans_obj, target=target, id=newName)
        except Exception:
            logger.warning("Could not move %s", "/".join(trans_obj.getPhysicalPath()))
            raise

        new_path = "/".join(moved.getPhysicalPath())
        result[lang] = new_path
        result[f"{lang}-old"] = old_path
        logger.info("Moved %s => %s", old_path, new_path)

    return result
