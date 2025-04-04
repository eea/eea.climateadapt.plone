import json

import requests
from lxml.html import tostring
from plone.api import portal
from plone.app.multilingual.interfaces import (
    ILanguageIndependentFieldsManager,
    ITranslationManager,
)
from plone.app.multilingual.manager import TranslationManager
from Testing.ZopeTestCase import utils as zopeUtils
from zope.component.hooks import setSite

from eea.climateadapt.browser.admin import force_unlock


class DummyPersistent(object):
    def getPhysicalPath(self):
        return "/"


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


def elements_to_text(children):
    return str("").join(tostring(f).decode("utf-8") for f in children)


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
            print(
                (
                    "plone.app.multilingual translation reindex",
                    trans_obj.absolute_url(relative=1),
                )
            )
            trans_obj.reindexObject()

    try:
        del site_portal.REQUEST
    except AttributeError:
        pass


# def translate_object_async(obj, language):
#     force_unlock(obj)
#     html = getMultiAdapter((obj, obj.REQUEST), name="tohtml")()
#     site = portal.getSite()
#     http_host = obj.REQUEST.environ.get(
#         "HTTP_X_FORWARDED_HOST", site.absolute_url())
#
#     queue_translate_volto_html(html, obj, http_host, language)
