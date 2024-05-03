import json
import logging
import time
from datetime import datetime

import transaction
from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.value import RichTextValue
from Products.Five.browser import BrowserView
from zope.site.hooks import getSite

from .. import (
    get_translated,
    retrieve_html_translation,
    translate_one_text_to_translation_storage,
)
from ..admin import is_obj_skipped_for_translation
from ..constants import source_richtext_types
from ..core import (
    get_translation_json_files,
    get_translation_object,
    get_translation_object_from_uid,
)
from ..utils import get_object_fields_values

logger = logging.getLogger("eea.climateadapt")


def trans_sync_workflow_state(site, request):
    """Publish translated items for a language and copy publishing and
    creation date from EN items.

    This used to be translation_step_5
    """

    # used for whole-site translation
    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    portal_type = request.get("portal_type", None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"

    catalog = site.portal_catalog
    search_data = {}
    search_data["path"] = "/cca/en"
    if uid:
        search_data["UID"] = uid
    if limit:
        search_data["sort_limit"] = limit
    if portal_type:
        search_data["portal_type"] = portal_type

    brains = catalog.searchResults(search_data)
    logger.info("Start publishing translated items...")

    obj_count = 0
    for brain in brains:
        if uid and uid != brain.UID:
            continue
        obj = brain.getObject()
        obj_count += 1
        logger.info("PROCESSING obj: %s", obj_count)

        try:
            translations = TranslationManager(obj).get_translations()
        except Exception:
            continue  # TODO: logging

        try:
            trans_obj = translations[language]
        except KeyError:
            logger.info("Missing translation for: %s", obj.absolute_url())
            continue

        try:
            state = api.content.get_state(obj)
        except WorkflowException:
            continue

        if state in ["published", "archived"]:
            if api.content.get_state(trans_obj) != state:
                wftool = getToolByName(trans_obj, "portal_workflow")
                logger.info("%s %s", state, trans_obj.absolute_url())
                if state == "published":
                    wftool.doActionFor(trans_obj, "publish")
                elif state == "archived":
                    wftool.doActionFor(trans_obj, "archive")

        if obj.EffectiveDate() != trans_obj.EffectiveDate():
            trans_obj.setEffectiveDate(obj.effective_date)
            trans_obj._p_changed = True
            trans_obj.reindexObject()

    logger.info("Finalize step 5")
    return "Finalize step 5"


def trans_copy_field_data(site, request, async_request=False):
    """Copy fields values from en to given language for language independent
        fields.
    TODO: this is used in a lot of places in code. It needs to be properly documented

    This used to be called translation_step_4
    """
    # used for whole-site translation

    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    portal_type = request.get("portal_type", None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"

    catalog = site.portal_catalog
    search_data = {}
    search_data["path"] = "/cca/en"
    if uid:
        search_data["UID"] = uid
    if limit:
        search_data["sort_limit"] = limit
    if portal_type:
        search_data["portal_type"] = portal_type

    brains = catalog.searchResults(search_data)
    logger.info("Start copying values for language independent fields...")

    obj_count = 0
    for brain in brains:
        if uid and uid != brain.UID:
            continue
        obj = brain.getObject()
        obj_count += 1
        logger.info("PROCESSING obj: %s", obj_count)

        try:
            translations = TranslationManager(obj).get_translations()
        except Exception:  # TODO: logging
            continue

        try:
            trans_obj = translations[language]
            # set REQUEST otherwise will give error
            # when executing trans_obj.setLayout()
            if async_request:  # not hasattr(trans_obj, 'REQUEST'):
                trans_obj.REQUEST = site.REQUEST
                obj.REQUEST = site.REQUEST
                # request = getattr(event.object, 'REQUEST', getRequest())

        except KeyError:
            logger.info("Missing translation for: %s", obj.absolute_url())
            continue

        reindex = False

        if obj.portal_type == "collective.cover.content":
            # Set propper collection for current language
            # WE supose to have only one cards_tile in the list of tiles
            reindex = handle_cover_step_4(obj, trans_obj, language, reindex)

        if obj.portal_type in ("Folder", "Document"):
            try:
                reindex = handle_folder_doc_step_4(
                    obj, trans_obj, reindex, async_request
                )
            except Exception:
                continue

        if reindex is True:
            if async_request:
                if hasattr(trans_obj, "REQUEST"):
                    del trans_obj.REQUEST

                if hasattr(obj, "REQUEST"):
                    del obj.REQUEST

            trans_obj._p_changed = True
            trans_obj.reindexObject()
            transaction.commit()  # TODO Improve. This is a fix for Event.

    logger.info("Finalize step 4")
    return "Finalize step 4"


def get_trans_obj_path_for_obj(obj):
    res = {}
    try:
        translations = TranslationManager(obj).get_translations()
    except Exception:
        logger.info("Error at getting translations for %s", obj.absolute_url())
        translations = []

    for language in translations:
        trans_obj = translations[language]
        trans_obj_url = trans_obj.absolute_url()

        res[language] = trans_obj_url

    return {"translated_obj_paths": res}


def get_translation_object_path(obj, language, site_url):
    trans_obj = get_translation_object(obj, language)
    if not trans_obj:
        return None
    trans_obj_url = trans_obj.absolute_url()
    return "/cca" + trans_obj_url.split(site_url)[-1]


def translation_step_1(site, request):
    """Save all items for translation in a json file"""
    limit = int(request.get("limit", 0))
    search_path = request.get("search_path", None)
    portal_type = request.get("portal_type", None)

    catalog = site.portal_catalog
    search_data = {}
    search_data["path"] = "/cca/en"
    if limit:
        search_data["sort_limit"] = limit
    if portal_type:
        search_data["portal_type"] = portal_type
    # if search_path:
    #    search_data['path'] = search_path

    brains = catalog.searchResults(search_data)
    # site_url = portal.getSite().absolute_url()
    logger.info("Start creating json files...")

    res = {}
    total_items = 0  # total translatable eng objects

    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        if is_obj_skipped_for_translation(obj):
            continue
        if search_path:
            if search_path not in obj_url:
                continue
        total_items += 1
        logger.info("PROCESS: %s %s", total_items, obj_url)

        data = get_object_fields_values(obj)

        # add the trans_obj_path for each language into the json
        translation_paths = get_trans_obj_path_for_obj(obj)
        data.update(translation_paths)

        json_object = json.dumps(data, indent=4)

        with open("/tmp/jsons/" + brain.UID + ".json", "w") as outfile:
            outfile.write(json_object)
        if obj.portal_type not in res:
            res[obj.portal_type] = 1
        else:
            res[obj.portal_type] += 1

    logger.info("DONE STEP 1. Res: %s", res)


class TranslateStep1(BrowserView):
    """Use this view to get a json files for all eng objects
    Usage: /admin-translate-step-1?limit=10&search_path=some-words-in-url
    Limit and search_path params are optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_1(getSite(), self.request)


def translation_step_2(site, request, force_uid=None):
    # used for whole-site translation
    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    offset = int(request.get("offset", 0))
    portal_type = request.get("portal_type", None)
    if force_uid:
        uid = force_uid

    """ Get all jsons objects in english and call etranslation for each field
        to be translated in specified language.
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    site_url = portal.getSite().absolute_url()
    json_files = get_translation_json_files(uid)

    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report = {}
    report["date"] = {
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end": None,
    }
    report["filter"] = {
        "language": language,
        "uid": uid,
        "limit": limit,
        "offset": offset,
        "portal_type": portal_type,
    }
    total_files = len(json_files)  # total translatable eng objs (not unique)
    nr_files = 0  # total translatable eng objects (not unique)
    nr_items = 0  # total translatable eng objects (not unique)
    nr_html_items = 0  # total translatable eng objects (not unique)
    nr_items_translated = 0  # found translated objects
    if limit:
        json_files.sort()
        json_files = json_files[offset : offset + limit]

    for json_file in json_files:
        file = open("/tmp/jsons/" + json_file, "r")
        json_content = file.read()
        json_data = json.loads(json_content)
        if portal_type and portal_type != json_data["portal_type"]:
            continue
        nr_files += 1
        # LOOP object tiles
        tile_html_fields = []
        if "tile" in json_data:
            for tile_id in json_data["tile"].keys():
                tile_data = json_data["tile"][tile_id]
                # LOOP tile text items
                for key in tile_data["item"].keys():
                    res = translate_one_text_to_translation_storage(
                        "EN", tile_data["item"][key], [language.upper()]
                    )
                    nr_items += 1
                    if "translated" in res:
                        nr_items_translated += 1
                # LOOP tile HTML items
                for key in tile_data["html"].keys():
                    value = tile_data["html"][key]
                    value = value.replace("\r", "")
                    value = value.replace("\n", "")
                    try:
                        _ = value + "test"
                    except UnicodeDecodeError:
                        value = value.decode("utf-8")
                    tile_html_fields.append(
                        {"tile_id": tile_id, "field": key, "value": value}
                    )
        # TILE HTML fields translate in one call
        if len(tile_html_fields):
            nr_html_items += 1
            obj = get_translation_object_from_uid(json_file, catalog)
            if obj is None:  # TODO: logging
                continue
            trans_obj_path = get_translation_object_path(obj, language, site_url)
            if not trans_obj_path:
                continue
            html_content = "<!doctype html>" + "<head><meta charset=utf-8></head><body>"
            for item in tile_html_fields:
                html_tile = (
                    "<div class='cca-translation-tile'"
                    + " data-field='"
                    + item["field"]
                    + "'"
                    + " data-tile-id='"
                    + item["tile_id"]
                    + "'"
                    + ">"
                    + item["value"]
                    + "</div>"
                )
                html_content += html_tile

            html_content += "</body></html>"
            html_content = html_content.encode("utf-8")
            retrieve_html_translation(
                "EN",
                html_content,
                trans_obj_path,
                language.upper(),
            )

        # LOOP object text items
        for key in json_data["item"].keys():
            res = translate_one_text_to_translation_storage(
                "EN", json_data["item"][key], [language.upper()]
            )
            nr_items += 1
            if "translated" in res:
                nr_items_translated += 1
        # LOOP object HTML items
        if len(json_data["html"]):
            nr_html_items += 1
            obj = get_translation_object_from_uid(json_file, catalog)
            if obj is None:  # TODO: logging
                continue
            trans_obj_path = get_translation_object_path(obj, language, site_url)
            if not trans_obj_path:
                continue

            html_content = "<!doctype html><head><meta charset=utf-8></head>"
            html_content += "<body>"

            for key in json_data["html"].keys():
                value = json_data["html"][key].replace("\r\n", "")
                html_section = (
                    "<div class='cca-translation-section'"
                    + " data-field='"
                    + key
                    + "'>"
                    + value
                    + "</div>"
                )

                html_content += html_section

            html_content += "</body></html>"
            html_content = html_content.encode("utf-8")
            res = retrieve_html_translation(
                "EN",
                html_content,
                trans_obj_path,
                language.upper(),
            )
        logger.info(
            "TransStep2 File  %s from %s, total files %s",
            nr_files,
            len(json_files),
            total_files,
        )
        if not force_uid:
            report["date"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report["response"] = {
                "items": {
                    "nr_files": nr_files,
                    "nr": nr_items,
                    "nr_already_translated": nr_items_translated,
                },
                "htmls": nr_html_items,
                "portal_type": portal_type,
            }
            report["total_files"] = total_files
            report["status"] = "Processing"

            json_object = json.dumps(report, indent=4)
            with open(
                "/tmp/translate_step_2_" + language + "_" + report_date + ".json", "w"
            ) as outfile:
                outfile.write(json_object)
        time.sleep(0.5)

    if not force_uid:
        report["date"]["end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report["status"] = "Done"
        report["response"] = {
            "items": {
                "nr_files": nr_files,
                "nr": nr_items,
                "nr_already_translated": nr_items_translated,
            },
            "htmls": nr_html_items,
        }
        report["total_files"] = total_files

        json_object = json.dumps(report, indent=4)
        with open(
            "/tmp/translate_step_2_" + language + "_" + report_date + ".json", "w"
        ) as outfile:
            outfile.write(json_object)

    logger.info(
        "Files: %s, Total: %s, Already translated: %s HtmlItems: %s",
        nr_files,
        nr_items,
        nr_items_translated,
        nr_html_items,
    )


class TranslateStep2(BrowserView):
    """Use this view to translate all json files to a language
    Usage: /admin-translate-step-2-old?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_2(getSite(), self.request)


def translation_step_3_one_file(json_file, language, catalog, portal_type=None):
    # used for whole-site translation
    obj = get_translation_object_from_uid(json_file, catalog)

    if obj is None:
        return  # TODO: logging

    trans_obj = get_translation_object(obj, language)
    if trans_obj is None:
        return

    file = open("/tmp/jsons/" + json_file, "r")
    json_content = file.read()
    json_data = json.loads(json_content)
    if portal_type and portal_type != json_data["portal_type"]:
        return
    have_change = False
    if "tile" in json_data:
        for tile_id in json_data["tile"].keys():
            tile_data = json_data["tile"][tile_id]
            tile_annot_id = "plone.tiles.data." + tile_id
            tile = trans_obj.__annotations__.get(tile_annot_id, None)
            if not tile:
                continue
            for key in tile_data["item"].keys():
                try:
                    update = tile.data
                except AttributeError:
                    update = tile
                translated_msg = get_translated(
                    tile_data["item"][key], language.upper()
                )
                if translated_msg:
                    if key == "title":
                        update[key] = translated_msg.encode("latin-1")
                    else:
                        try:
                            update[key] = translated_msg.encode("latin-1")
                        except Exception:
                            update[key] = translated_msg
                    have_change = True
                # tile.data.update(update)
                trans_obj.__annotations__[tile_annot_id] = update

    for key in json_data["item"].keys():
        translated_msg = get_translated(json_data["item"][key], language.upper())

        if translated_msg:
            encoded_text = translated_msg.encode("latin-1")

            if key == "source" and obj.portal_type in source_richtext_types:
                setattr(trans_obj, key, getattr(obj, key))
                # solves Can not convert 'Elsevier' to an IRichTextValue
                setattr(trans_obj, key, RichTextValue(encoded_text))
                have_change = True
            else:
                try:
                    setattr(trans_obj, key, encoded_text)
                    have_change = True
                except AttributeError:
                    logger.info(
                        "AttributeError for obj: %s key: %s", obj.absolute_url(), key
                    )
    if have_change:
        trans_obj._p_changed = True
        trans_obj.reindexObject()


def translation_step_3(site, request):
    """Get all jsons objects in english and overwrite targeted language
    object with translations.
    """
    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    offset = int(request.get("offset", 0))
    portal_type = request.get("portal_type", None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    json_files = get_translation_json_files(uid)
    total_files = len(json_files)  # total translatable eng objs (not unique)

    report_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report = {}
    report["date"] = {
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end": None,
    }
    report["filter"] = {
        "language": language,
        "uid": uid,
        "limit": limit,
        "offset": offset,
        "portal_type": portal_type,
    }
    report["total_files"] = total_files

    if limit:
        json_files.sort()
        json_files = json_files[offset : offset + limit]

    nr_files = 0  # total translatable eng objects (not unique)

    for json_file in json_files:
        nr_files += 1
        logger.info("PROCESSING file: %s", nr_files)

        try:
            translation_step_3_one_file(json_file, language, catalog, portal_type)
            transaction.commit()  # make sure tiles are saved (encoding issue)
        except Exception as err:
            logger.info("ERROR")  # TODO improve this
            logger.info(err)

        report["date"]["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report["response"] = {"last_item": json_file, "files_processd": nr_files}
        report["status"] = "Processing"

        json_object = json.dumps(report, indent=4)
        with open(
            "/tmp/translate_step_3_" + language + "_" + report_date + ".json", "w"
        ) as outfile:
            outfile.write(json_object)

    report["date"]["end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report["status"] = "Done"

    json_object = json.dumps(report, indent=4)
    with open(
        "/tmp/translate_step_3_" + language + "_" + report_date + ".json", "w"
    ) as outfile:
        outfile.write(json_object)

    logger.info("Finalize step 3")


class TranslateStep3(BrowserView):
    """Use this view to save the values from annotation in objects fields
    Usage: /admin-translate-step-3?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_step_3(getSite(), self.request)


class TranslateStep4(BrowserView):
    """Use this view to copy fields values that are language independent

    Usage: /admin-translate-step-4?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return trans_copy_field_data(getSite(), self.request)


class TranslateStep5(BrowserView):
    """Use this view to publish all translated items for a language
    and copy the publishing and creation date from EN items.

    Usage: /admin-translate-step-5?language=ro&uid=ABCDEF
    uid is optional
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return trans_sync_workflow_state(getSite(), self.request)
