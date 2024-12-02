from plone.app.multilingual.interfaces import ILanguageIndependentFieldsManager
import base64
import json
import logging
import os

import requests
from Acquisition import aq_inner, aq_parent
from lxml.html import tostring
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
from Testing.ZopeTestCase import utils as zopeUtils
from zeep import Client
from zeep.wsse.username import UsernameToken
from zope.component.hooks import setSite
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder
from plone.app.multilingual.interfaces import ITranslationManager

from eea.climateadapt.browser.admin import force_unlock

from .constants import LANGUAGE_INDEPENDENT_FIELDS

env = os.environ.get

TRANS_USERNAME = "ipetchesi"  # TODO: get another username?
MARINE_PASS = env("MARINE_PASS", "")
SERVICE_URL = "https://webgate.ec.europa.eu/etranslation/si/translate"

logger = logging.getLogger("eea.climateadapt")

SLATE_CONVERTER = "http://converter:8000/html"
BLOCKS_CONVERTER = "http://converter:8000/blocks2html"
CONTENT_CONVERTER = "http://converter:8000/html2content"


class DummyPersistent(object):
    def getPhysicalPath(self):
        return "/"


def call_etranslation_service(
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
        logger.warning("Using localhost, won't retrieve translation for: %s", html)

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


def get_translation_object(obj, language):
    """Returns the translation object for a given language"""
    try:
        translations = TranslationManager(obj).get_translations()
    except Exception:
        if language == "en":  # temporary solution to have EN site working
            return obj  # TODO: better fix
        return None

    if language not in translations:
        return None
    trans_obj = translations[language]
    return trans_obj


def sync_obj_layout(obj, trans_obj, reindex, async_request):
    """Used by save_html_volto"""
    force_unlock(obj)

    layout_en = obj.getLayout()
    default_view_en = obj.getDefaultPage()
    layout_default_view_en = None

    if default_view_en:
        try:
            trans_obj.setDefaultPage(default_view_en)
            reindex = True
        except Exception:
            logger.info("Can't set default page for: %s", trans_obj.absolute_url())

    if not reindex:
        reindex = True
        trans_obj.setLayout(layout_en)

    if default_view_en is not None:
        layout_default_view_en = obj[default_view_en].getLayout()

    # set the layout of the translated object to match the EN object

    # also set the layout of the default view
    if layout_default_view_en:
        try:
            trans_obj[default_view_en].setLayout(layout_default_view_en)
        except Exception:
            logger.info("Can't set layout for: %s", trans_obj.absolute_url())
            raise

    if async_request:
        if hasattr(trans_obj, "REQUEST"):
            del trans_obj.REQUEST

        if hasattr(obj, "REQUEST"):
            del obj.REQUEST


handle_folder_doc_step_4 = sync_obj_layout  # BBB


def check_ancestors_path_exists(obj, language, site_portal):
    """Create full path for a object"""

    parent = aq_parent(aq_inner(obj))
    path = parent.getPhysicalPath()

    if len(path) <= 2:  # aborting, we've reached bottom
        return True

    translations = TranslationManager(parent).get_translations()
    if language not in translations:
        # TODO, what if the parent path already exist in language
        # but is not linked in translation manager
        setup_translation_object(parent, language, site_portal)


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


def get_all_objs(container):
    """Get the container's objects"""
    all_objs = []

    def get_objs(context):
        contents = api.content.find(context=context, depth=1)
        for item in contents:
            all_objs.append(item)

        for item in contents:
            get_objs(item.getObject())

    get_objs(container)

    return all_objs


def is_volto_context(context):
    volto_contexts = ["/en/mission", "/en/observatory"]
    for value in volto_contexts:
        if value in context.absolute_url():
            return True
    return False


def sync_translation_state(trans_obj, en_obj):
    state = None

    try:
        state = api.content.get_state(en_obj)
    except WorkflowException:
        logger.error("Can't get state for original object: %s", en_obj)
        pass

    if state in ["published", "archived"]:
        if api.content.get_state(trans_obj) != state:
            wftool = getToolByName(trans_obj, "portal_workflow")
            logger.info("%s %s", state, trans_obj.absolute_url())
            if state == "published":
                wftool.doActionFor(trans_obj, "publish")
            elif state == "archived":
                wftool.doActionFor(trans_obj, "archive")

    if en_obj.EffectiveDate() != trans_obj.EffectiveDate():
        trans_obj.setEffectiveDate(en_obj.effective_date)
        trans_obj._p_changed = True

    if en_obj.__ac_local_roles__ != trans_obj.__ac_local_roles__:
        trans_obj._p_changed = True
        trans_obj.__ac_local_roles__ = en_obj.__ac_local_roles__


def wrap_in_aquisition(obj_path, portal_obj):
    portal_path = portal_obj.getPhysicalPath()
    bits = obj_path.split("/")[len(portal_path) :]

    base = portal_obj
    obj = base

    for bit in bits:
        obj = base.restrictedTraverse(bit).__of__(base)
        base = obj

    return obj


def setup_site_portal(options):
    environ = {
        "SERVER_NAME": options["http_host"],
        "SERVER_PORT": 443,
        "REQUEST_METHOD": "POST",
    }
    site_portal = portal.get()

    if not hasattr(site_portal, "REQUEST"):
        zopeUtils._Z2HOST = options["http_host"]
        site_portal = zopeUtils.makerequest(site_portal, environ)
        server_url = site_portal.REQUEST.other["SERVER_URL"].replace("http", "https")
        site_portal.REQUEST.other["SERVER_URL"] = server_url
        setSite(site_portal)
        # context.REQUEST['PARENTS'] = [context]

        # for k, v in request_vars.items():
        #     site_portal.REQUEST.set(k, v)

    return site_portal


def execute_translate_async(context, **kwargs):
    """Async Job: triggers the call to eTranslation

    Creates the translation object, if it doesn't exist
    """
    en_obj_path = kwargs["path"]
    options = kwargs["options"]
    language = kwargs["language"]

    # print("Args", en_obj_path, options, language)
    # en_obj_path = "/".join(en_obj.getPhysicalPath())

    site_portal = setup_site_portal(options)

    # this causes the modified event in plone.app.multilingual to skip some processing which otherwise crashes
    site_portal.REQUEST.translation_info = {"tg": True}

    en_obj = site_portal.restrictedTraverse(en_obj_path)
    en_obj = wrap_in_aquisition(en_obj_path, site_portal)

    # trans_obj = site_portal.restrictedTraverse(trans_obj_path)
    trans_obj = setup_translation_object(en_obj, language, site_portal)
    trans_obj_path = "/".join(trans_obj.getPhysicalPath())

    call_etranslation_service(
        options["http_host"],
        "en",
        options["html_content"].encode("utf-8"),
        trans_obj_path,
        target_languages=language.upper(),
    )

    try:
        del site_portal.REQUEST
        del en_obj.REQUEST
        del trans_obj.REQUEST
    except AttributeError:
        pass

    logger.info("Async translate for object %s", options["obj_url"])
    return "Finished"


def handle_link(en_obj, trans_obj):
    link = getattr(en_obj, "remoteUrl", None)
    logger.info("Fixing link %s (%s)", trans_obj.absolute_url(), link)
    if link:
        link = link.replace("/en/", "/%s/" % trans_obj.language)
        logger.info("Fixed with: %s", link)
        trans_obj.remoteUrl = link
    trans_obj._p_changed = True


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


def elements_to_text(children):
    return str("").join(tostring(f).decode("utf-8") for f in children)


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


def ingest_html(trans_obj, html):
    """Used by the translation callback"""

    force_unlock(trans_obj)
    fielddata = get_content_from_html(html, language=trans_obj.language)

    translations = TranslationManager(trans_obj).get_translations()

    if "en" not in translations:
        msg = (
            "Could not find canonical for this object %s, aborting. "
            "Check its translation group" % "/".join(trans_obj.getPhysicalPath())
        )

        logger.warning(msg)
        raise ValueError(msg)

    en_obj = translations["en"]  # hardcoded, should use canonical

    save_field_data(en_obj, trans_obj, fielddata)

    copy_missing_interfaces(en_obj, trans_obj)

    if trans_obj.portal_type in ("Folder", "Document"):
        handle_folder_doc_step_4(en_obj, trans_obj, False, False)
    if trans_obj.portal_type in ["Link"]:
        handle_link(en_obj, trans_obj)

    # TODO: sync workflow state

    trans_obj._p_changed = True
    trans_obj.reindexObject()


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


def sync_language_independent_fields(context, en_obj_path, options):
    """Async Job: copies the language independent fields to all translations"""
    site_portal = setup_site_portal(options)
    environ = {
        "SERVER_NAME": options["http_host"],
        "SERVER_PORT": 443,
        "REQUEST_METHOD": "POST",
    }

    if not hasattr(site_portal, "REQUEST"):
        zopeUtils._Z2HOST = options["http_host"]
        site_portal = zopeUtils.makerequest(site_portal, environ)
        server_url = site_portal.REQUEST.other["SERVER_URL"].replace("http", "https")
        site_portal.REQUEST.other["SERVER_URL"] = server_url
        setSite(site_portal)

    content = wrap_in_aquisition(en_obj_path, site_portal)
    fieldmanager = ILanguageIndependentFieldsManager(content)

    transmanager = ITranslationManager(content)
    translations = transmanager.get_translated_languages()
    translations.remove("en")

    for translation in translations:
        trans_obj = transmanager.get_translation(translation)
        if fieldmanager.copy_fields(trans_obj):
            print((
                "plone.app.multilingual translation reindex",
                trans_obj.absolute_url(relative=1),
            ))
            trans_obj.reindexObject()

    try:
        del site_portal.REQUEST
    except AttributeError:
        pass
