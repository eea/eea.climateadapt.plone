from Acquisition import aq_inner, aq_parent
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from Testing.ZopeTestCase import utils as zopeUtils
from collections import defaultdict
from datetime import datetime
from eea.climateadapt.browser.admin import force_unlock
from plone import api
from plone.api import content, portal
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.behavior.interfaces import IBehaviorAssignable
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder
import json
import logging
import os
import time
import transaction

from .translate_obj import translate_obj
from .utils import get_object_fields_values, is_json
from .constants import source_richtext_types, contenttype_language_independent_fields
from . import (
    get_translated,
    retrieve_html_translation,
    translate_one_text_to_translation_storage,
    retrieve_volto_html_translation
)

# steps => used to translate the entire website
# translate in one step (when object is published)
# translate async => manual action

logger = logging.getLogger("eea.climateadapt")


def initiate_translations(site, skip=0, version=None, language=None):
    # used for whole-site translation
    skip = int(skip)
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    if version is None:
        return "Missing translation version. Status: /admin-translation-status"
    version = int(version)
    catalog = site.portal_catalog
    count = -1
    res = catalog.searchResults(path="/cca/en")
    errors = []
    debug_skip = False
    debug_skip_number = skip  # do not translate first objects

    if skip > 0:
        debug_skip = True
    total_objs = len(res)

    translate_only = False
    only = []  # Example: ['Event', 'cca-event']
    if len(only) > 0:
        translate_only = True  # translate only the specified content types

    for brain in res:
        count += 1

        if debug_skip is True and count < debug_skip_number:
            continue

        if translate_only is True and brain.portal_type not in only:
            continue

        logger.info("--------------------------------------------------------")
        logger.info(count)
        logger.info(total_objs)
        logger.info("--------------------------------------------------------")

        if brain.getPath() == "/cca/en" or brain.portal_type in ["LIF", "LRF"]:
            continue

        obj = brain.getObject()

        try:
            result = translate_obj(obj, language, version)
        except Exception as err:
            result = {"errors": [err]}
            logger.info(err)
            # errors.append(err)
            import pdb

            pdb.set_trace()

        t_errors = result.get("errors", []) if result is not None else []
        if len(t_errors) > 0:
            for error in t_errors:
                if error not in errors:
                    errors.append(error)

        if count % 20 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    logger.info("DONE")
    logger.info(errors)
    transaction.commit()


def translations_status(site, language=None):
    if language is None:
        return "Missing language."

    path = "/cca/" + language
    catalog = site.portal_catalog
    brains = catalog.searchResults(path=path)

    versions = defaultdict(int)
    template = "<p>{} at version {}</p>"
    logger.info("Translations status:")

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, "version", 0))
        versions[obj_version] += 1

    res = []
    for k, v in versions.items():
        res.append(template.format(v, k))

    logger.info(res)
    return "".join(res)


def verify_cloned_language(site, language=None):
    """Get all objects in english and check if all of them are cloned for
    given language. Also make sure all paths are similar.
    Correct:
        /cca/en/obj-path
        /cca/ro/obj-path
    Wrong:
        /cca/en/obj-path
        /cca/ro/obj-path-ro-ro-ro
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    brains = catalog.searchResults(path="/cca/en")
    site_url = portal.getSite().absolute_url()
    logger.info("I will list the missing objects if any. Checking...")

    res = []
    found = 0  # translation found with correct path
    found_changed = 0  # translation found but with different path
    not_found = 0  # translation not found
    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        obj_path = "/cca" + obj_url.split(site_url)[-1]
        prefix = "/cca/" + language.lower() + "/"
        trans_obj_path = obj_path.replace("/cca/en/", prefix)
        try:
            trans_obj = site.unrestrictedTraverse(trans_obj_path)
            found += 1
        except Exception:
            res.append(trans_obj_path)
            translations = TranslationManager(obj).get_translations()
            if language in translations:
                trans_obj = translations[language]
                new_url = trans_obj.absolute_url()
                res.append("Found as: " + new_url)
                found_changed += 1
                logger.info(trans_obj_path)
                logger.info("Found as %s", new_url)
            else:
                not_found += 1
                res.append("Not found.")
                logger.info("Not found: %s", trans_obj_path)

    logger.info(
        "Found: %s. Found with different path: %s. Not found: %s.",
        found,
        found_changed,
        not_found,
    )

    return "\n".join(res)


def fix_urls_for_translated_content(site, language=None):
    """We want to have the same urls for translated content as for EN
    Example:
        /cca/en/test-page-en
        /cca/fr/test-page will become /cca/fr/test-page-en
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    brains = catalog.searchResults(path="/cca/en")
    site_url = portal.getSite().absolute_url()
    logger.info("Checking for urls to be fixed...")

    solved = 0
    not_solved = {
        "different_path_same_id": [],
        "cannot_rename_id": [],
        "missing_translation": [],
    }

    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        obj_path = "/cca" + obj_url.split(site_url)[-1]
        prefix = "/cca/" + language.lower() + "/"
        trans_obj_path = obj_path.replace("/cca/en/", prefix)
        try:
            trans_obj = site.unrestrictedTraverse(trans_obj_path)
        except Exception:
            # the urls doesn't match
            logger.info("PROBLEM: %s", trans_obj_path)
            translations = TranslationManager(obj).get_translations()
            if language in translations:
                trans_obj = translations[language]
                new_url = trans_obj.absolute_url()
                logger.info("FOUND %s", new_url)
                try:
                    if trans_obj.id != obj.id:
                        # ids doesn't match
                        trans_obj.aq_parent.manage_renameObject(
                            trans_obj.id, obj.id)
                        logger.info("SOLVED")
                        solved += 1
                    else:
                        # parent path doesn't match
                        logger.info("NOT SOLVED. Different path, same id.")
                        not_solved["different_path_same_id"].append(
                            (obj_url, trans_obj.absolute_url())
                        )
                except Exception:
                    # id not available
                    logger.info("NOT SOLVED. Cannot rename, id not available.")
                    not_solved["cannot_rename_id"].append(
                        (obj_url, trans_obj.absolute_url())
                    )
            else:
                # missing translation
                logger.info("NOT SOLVED. Missing translation: %s",
                            trans_obj_path)
                not_solved["missing_translation"].append(obj_url)

    logger.info("DONE. Solved: %s", solved)
    logger.info("Not solved:")
    logger.info(not_solved)
    return {"solved": solved, "not_solved": not_solved}


def verify_translation_fields(site, request):
    language = request.get("language", None)
    uid = request.get("uid", None)
    stop_pdb = request.get("stop_pdb", None)
    portal_type = request.get("portal_type", None)
    """ Get all objects in english and check if all of them are cloned for
        given language and with fields filled.
    """
    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    catalog = site.portal_catalog
    # brains = catalog.searchResults(path='/cca/en')
    catalogSearch = {}
    catalogSearch["path"] = "/cca/en"
    if uid:
        catalogSearch["UID"] = uid
    brains = catalog.searchResults(catalogSearch)
    site_url = portal.getSite().absolute_url()
    logger.info("I will list the missing translation fields. Checking...")

    res = []
    total_items = 0  # total translatable eng objects
    found = 0  # found end objects
    found_missing = 0  # missing at least one attribute
    not_found = 0  # eng obj not found
    missing_values = 0  # count the missing field values

    report = {}
    report_detalied = []
    skip_items = [".jpg", ".pdf", ".png"]
    skip_fields = ["sync_uid", "allow_discussion"]
    # skip_types = ['File', 'Image']

    for brain in brains:
        obj = brain.getObject()
        if portal_type and portal_type != obj.portal_type:
            continue
        if is_obj_skipped_for_translation(obj):
            continue

        obj_url = obj.absolute_url()

        # if obj.portal_type in skip_types:
        #     continue

        if obj.portal_type not in report:
            report[obj.portal_type] = {}

        if any(skip_item in obj_url for skip_item in skip_items):
            continue
        total_items += 1
        obj_path = "/cca" + obj_url.split(site_url)[-1]
        translations = TranslationManager(obj).get_translations()
        if language not in translations:
            logger.info("Not found: %s", obj_path)
            not_found += 1
            continue
        trans_obj = translations[language]

        # get behavior fields and values
        behavior_assignable = IBehaviorAssignable(obj)
        fields = {}
        if behavior_assignable:
            behaviors = behavior_assignable.enumerateBehaviors()
            for behavior in behaviors:
                for k, v in getFieldsInOrder(behavior.interface):
                    fields.update({k: v})
        for k, v in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
            fields.update({k: v})

        logger.info("%s URL: %s", found, trans_obj.absolute_url())
        fields_missing = []
        if stop_pdb:
            import pdb

            pdb.set_trace()
        for field in fields.keys():
            if field in skip_fields:
                continue
            # TODO: check if we need to log if this is FALSE
            if not hasattr(obj, field):
                continue
            if not hasattr(trans_obj, field):
                fields_missing.append(field)
                continue
            mark_field = False
            if isinstance(getattr(obj, field), RichTextValue):
                obj_val = getattr(obj, field).output
                trans_obj_val = ""
                if isinstance(getattr(trans_obj, field), RichTextValue):
                    trans_obj_val = getattr(trans_obj, field).output
                else:
                    trans_obj_val = getattr(trans_obj, field, None)
                    if not trans_obj_val:
                        trans_obj_val = ""
                if len(obj_val) and 0 == len(trans_obj_val):
                    mark_field = True
            elif isinstance(getattr(obj, field), unicode):
                obj_val = getattr(obj, field)
                trans_obj_val = ""
                if isinstance(getattr(trans_obj, field), unicode):
                    trans_obj_val = getattr(trans_obj, field)
                elif isinstance(getattr(trans_obj, field), RichTextValue):
                    trans_obj_val = getattr(trans_obj, field).output
                else:
                    trans_obj_val = getattr(trans_obj, field, "")
                    if not trans_obj_val:
                        trans_obj_val = ""
                if len(obj_val) and 0 == len(trans_obj_val):
                    mark_field = True
            else:
                missing = object()
                if (
                    not mark_field
                    and getattr(obj, field, missing) not in (missing, None)
                    and getattr(trans_obj, field, missing) in (missing, None)
                ):
                    mark_field = True
            if mark_field:
                fields_missing.append(field)
                missing_values += 1

                if field not in report[obj.portal_type]:
                    report[obj.portal_type][field] = 0

                prev_value = report[obj.portal_type][field]
                report[obj.portal_type][field] = prev_value + 1

        if len(fields_missing):
            logger.info(
                "FIELDS NOT SET: %s %s", trans_obj.absolute_url(), fields_missing
            )
            report_detalied.append(
                {
                    "url": trans_obj.absolute_url(),
                    "brain_uid": brain.UID,
                    "missing": fields_missing,
                    "portal_type": trans_obj.portal_type,
                }
            )
            found_missing += 1

        found += 1

    logger.info(
        "Items: %s, With correct data: %s. With missing data: %s. Not found: %s. Missing values: %s",
        total_items,
        found,
        found_missing,
        not_found,
        missing_values,
    )

    report["_details"] = report_detalied
    report["_stats"] = {
        "file": total_items,
        "found": found,
        "found_missing": found_missing,
        "not_found": not_found,
        "missing_value": missing_values,
    }
    json_object = json.dumps(report, indent=4)
    with open("/tmp/translation_report.json", "w") as outfile:
        outfile.write(json_object)

    return "\n".join(res)


def is_obj_skipped_for_translation(obj):
    # skip by portal types
    if obj.portal_type in ["eea.climateadapt.city_profile", "LIF"]:
        return True

    # DO NOT SKIP, images or pdfs from case-studies have description and title
    # fields those are needed to be translated (or at least to be copied)
    # skip by string in path
    # skip_path_items = ['.jpg','.pdf','.png']
    # obj_url = obj.absolute_url()
    # if any(skip_item in obj_url for skip_item in skip_path_items):
    # return True

    # TODO: add here archived and other rules
    return False


def get_translation_object(obj, language):
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


def get_translation_object_path(obj, language, site_url):
    trans_obj = get_translation_object(obj, language)
    if not trans_obj:
        return None
    trans_obj_url = trans_obj.absolute_url()
    return "/cca" + trans_obj_url.split(site_url)[-1]


def get_translation_object_from_uid(json_uid_file, catalog):
    brains = catalog.searchResults(UID=json_uid_file.replace(".json", ""))
    if 0 == len(brains):
        return None
    return brains[0].getObject()


def get_translation_json_files(uid=None):
    json_files = []
    if uid:
        if os.path.exists("/tmp/jsons/" + str(uid) + ".json"):
            json_files.append(str(uid) + ".json")
    else:
        json_files = os.listdir("/tmp/jsons/")
    return json_files


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
        json_files = json_files[offset: offset + limit]

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
            trans_obj_path = get_translation_object_path(
                obj, language, site_url)
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
            trans_obj_path = get_translation_object_path(
                obj, language, site_url)
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
            report["date"]["last_update"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
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
        translated_msg = get_translated(
            json_data["item"][key], language.upper())

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
        json_files = json_files[offset: offset + limit]

    nr_files = 0  # total translatable eng objects (not unique)

    for json_file in json_files:
        nr_files += 1
        logger.info("PROCESSING file: %s", nr_files)

        try:
            translation_step_3_one_file(
                json_file, language, catalog, portal_type)
            transaction.commit()  # make sure tiles are saved (encoding issue)
        except Exception as err:
            logger.info("ERROR")  # TODO improve this
            logger.info(err)

        report["date"]["last_update"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
        report["response"] = {
            "last_item": json_file, "files_processd": nr_files}
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


def translation_step_4(site, request, async_request=False):
    # used for whole-site translation
    """Copy fields values from en to given language for language independent
    fields.
    """
    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    # offset = int(request.get("offset", 0))
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

    # brains = catalog.searchResults(path='/cca/en', sort_limit=limit)
    brains = catalog.searchResults(search_data)

    # brains = catalog.searchResults(path='/cca/en')
    # site_url = portal.getSite().absolute_url()
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
        except:  # TODO: logging
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
            try:
                data_tiles = obj.get_tiles()
                for data_tile in data_tiles:
                    if data_tile["type"] == "eea.climateadapt.cards_tile":
                        data_trans_tiles = obj.get_tiles()
                        for data_trans_tile in data_trans_tiles:
                            if data_trans_tile["type"] == "eea.climateadapt.cards_tile":
                                tile = obj.get_tile(data_tile["id"])
                                try:
                                    trans_tile = trans_obj.get_tile(
                                        data_trans_tile["id"]
                                    )
                                except ValueError:
                                    logger.info("Tile not found.")
                                    trans_tile = None

                                if trans_tile is not None:
                                    collection_obj = uuidToObject(
                                        tile.data["uuid"])
                                    collection_trans_obj = get_translation_object(
                                        collection_obj, language
                                    )

                                    dataManager = ITileDataManager(trans_tile)

                                    temp = dataManager.get()
                                    try:
                                        temp["uuid"] = IUUID(
                                            collection_trans_obj)
                                    except TypeError:
                                        logger.info("Collection not found.")

                                    dataManager.set(temp)
                    if data_tile["type"] == "eea.climateadapt.relevant_acecontent":
                        tile = obj.get_tile(data_tile["id"])
                        tile_type = get_tile_type(tile, obj, trans_obj)
                        from_tile = obj.restrictedTraverse(
                            "@@{0}/{1}".format(tile_type, tile.id)
                        )
                        to_tile = trans_obj.restrictedTraverse(
                            "@@{0}/{1}".format(tile_type, tile.id)
                        )

                        from_data_mgr = ITileDataManager(from_tile)
                        to_data_mgr = ITileDataManager(to_tile)
                        from_data = from_data_mgr.get()

                        trans_tile = trans_obj.get_tile(data_tile["id"])
                        from_data["title"] = trans_tile.data["title"]
                        to_data_mgr.set(from_data)

            except KeyError:
                logger.info("Problem setting collection in tile for language")

            force_unlock(obj)
            layout_en = obj.getLayout()
            if layout_en:
                reindex = True
                trans_obj.setLayout(layout_en)

        if obj.portal_type in ("Folder", "Document"):
            force_unlock(obj)

            layout_en = obj.getLayout()
            default_view_en = obj.getDefaultPage()
            layout_default_view_en = None
            if default_view_en:
                try:
                    trans_obj.setDefaultPage(default_view_en)
                    reindex = True
                except:
                    logger.info(
                        "Can't set default page for: %s", trans_obj.absolute_url()
                    )
            if not reindex:
                reindex = True
                trans_obj.setLayout(layout_en)

            if default_view_en is not None:
                layout_default_view_en = obj[default_view_en].getLayout()

            # set the layout of the translated object to match the EN object

            # also set the layout of the default view
            if layout_default_view_en:
                try:
                    trans_obj[default_view_en].setLayout(
                        layout_default_view_en)
                except:
                    logger.info("Can't set layout for: %s",
                                trans_obj.absolute_url())
                    continue

            if async_request:
                if hasattr(trans_obj, "REQUEST"):
                    del trans_obj.REQUEST

                if hasattr(obj, "REQUEST"):
                    del obj.REQUEST

            trans_obj._p_changed = True
            trans_obj.reindexObject()

        if obj.portal_type in contenttype_language_independent_fields:
            force_unlock(obj)
            obj_url = obj.absolute_url()
            logger.info("PROCESS: %s", obj_url)

            translations = None
            try:
                translations = TranslationManager(obj).get_translations()
            except:
                pass

            if translations is None:
                continue

            try:
                trans_obj = translations[language]
            except KeyError:
                logger.info("Missing translation for: %s", obj_url)
                continue

            # fields = contenttype_language_independent_fields[obj.portal_type]
            # for key in fields:
            #     logger.info("Field: %s", key)
            #
            #     if key == "start":
            #         trans_obj.start = obj.start
            #         reindex = True
            #     elif key == "end":
            #         trans_obj.end = obj.end
            #         reindex = True
            #     elif key == "effective":
            #         trans_obj.setEffectiveDate(obj.effective_date)
            #         reindex = True
            #     elif key == "timezone":
            #         trans_obj.timezone = obj.timezone
            #         reindex = True
            #     else:
            #         try:
            #             setattr(trans_obj, key, getattr(obj, key))
            #             reindex = True
            #         except Exception:
            #             logger.info("Skip: %s %s", obj.portal_type, key)

        if reindex is True:
            if async_request:
                if hasattr(trans_obj, "REQUEST"):
                    del trans_obj.REQUEST

                if hasattr(obj, "REQUEST"):
                    del obj.REQUEST

            trans_obj._p_changed = True
            trans_obj.reindexObject()
            transaction.commit()  # TODO Improve. This is a fix for Event.
            continue

    logger.info("Finalize step 4")
    return "Finalize step 4"


def translation_step_5(site, request):
    # used for whole-site translation
    """Publish translated items for a language and copy publishing and
    creation date from EN items.
    """
    language = request.get("language", None)
    uid = request.get("uid", None)
    limit = int(request.get("limit", 0))
    # offset = int(request.get("offset", 0))
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


def translation_repaire(site, request):
    """Get all jsons objects in english and overwrite targeted language
    object with translations.
    """
    language = request.get("language", None)
    file = request.get("file", None)
    # uid = request.get("uid", None)
    # limit = int(request.get("limit", 0))
    # offset = int(request.get("offset", 0))
    # portal_type = request.get("portal_type", None)
    stop_pdb = request.get("stop_pdb", None)

    if language is None:
        return "Missing language parameter. (Example: ?language=it)"
    if file is None:
        return "Missing file parameter. (Example: ?file=ABC will process /tmp/ABC.json)"
    file = open("/tmp/" + file + ".json", "r")
    json_content = file.read()
    if not is_json(json_content):
        return "Looks like we the file is not valid json"
    json_data = json.loads(json_content)

    if "_details" not in json_data:
        return "Details key was not found in json"

    items = json_data["_details"]
    if stop_pdb:
        import pdb

        pdb.set_trace()
    for item in items:
        translation_step_2(site, request, item["brain_uid"])


def translation_repaire_step_3(site, request):
    """Get all jsons objects in english and overwrite targeted language
    object with translations.
    """
    print(site, request)
    # language = request.get("language", None)
    # file = request.get("file", None)
    # uid = request.get("uid", None)
    # # limit = int(request.get("limit", 0))
    # # offset = int(request.get("offset", 0))
    # portal_type = request.get("portal_type", None)
    # stop_pdb = request.get("stop_pdb", None)
    #
    # if language is None:
    #     return "Missing language parameter. (Example: ?language=it)"
    # if file is None:
    #     return "Missing file parameter. (Example: ?file=ABC will process /tmp/ABC.json)"
    # file = open("/tmp/" + file + ".json", "r")
    # json_content = file.read()
    # if not is_json(json_content):
    #     return "Looks like we the file is not valid json"
    # json_data = json.loads(json_content)
    #
    # if "_details" not in json_data:
    #     return "Details key was not found in json"
    #
    # items = json_data["_details"]
    # if stop_pdb:
    #     import pdb
    #
    #     pdb.set_trace()
    #
    # catalog = site.portal_catalog

    # for item in items:
    #     if uid and uid != brain.UID:
    #         continue
    #     if portal_type and portal_type != item["portal_type"]:
    #         continue
    #     if stop_pdb:
    #         import pdb
    #
    #         pdb.set_trace()
    #     translation_step_3_one_file(
    #         item["brain_uid"] + ".json", language, catalog, portal_type
    #     )


def translation_list_type_fields(site):
    # used for whole-site translation
    """Show each field for each type"""
    catalog = site.portal_catalog
    # TODO: remove this, it is jsut for demo purpose
    limit = 10000
    brains = catalog.searchResults(path="/cca/en", sort_limit=limit)
    logger.info("I will start to create json files. Checking...")

    res = {}

    for brain in brains:
        obj = brain.getObject()
        obj_url = obj.absolute_url()
        logger.info("PROCESS: %s", obj_url)
        if is_obj_skipped_for_translation(obj):
            continue
        data = get_object_fields_values(obj)

        if obj.portal_type == "collective.cover.content":
            if obj.portal_type not in res:
                res[obj.portal_type] = {}
            tiles_id = obj.list_tiles()
            for tile_id in tiles_id:
                tile = obj.get_tile(tile_id)
                tile_name = tile.__class__.__name__
                if tile_name not in res[obj.portal_type]:
                    res[obj.portal_type][tile_name] = {}
                for field in tile.data.keys():
                    if field not in res[obj.portal_type][tile_name]:
                        res[obj.portal_type][tile_name][field] = []
                    if len(res[obj.portal_type][tile_name][field]) < 5:
                        res[obj.portal_type][tile_name][field].append(obj_url)
        else:
            if obj.portal_type not in res:
                res[obj.portal_type] = {"item": [], "html": []}
            for key in data["item"]:
                if key not in res[obj.portal_type]["item"]:
                    res[obj.portal_type]["item"].append(key)
            for key in data["html"]:
                if key not in res[obj.portal_type]["html"]:
                    res[obj.portal_type]["html"].append(key)

    json_object = json.dumps(res, indent=4)

    with open("/tmp/portal_type_fields.json", "w") as outfile:
        outfile.write(json_object)


def translations_status_by_version(site, version=0, language=None):
    """Show the list of urls of a version and language"""
    if language is None:
        return "Missing language."

    path = "/cca/" + language
    version = int(version)
    catalog = site.portal_catalog
    brains = catalog.searchResults()
    brains = catalog.searchResults(path=path)

    res = []
    template = "<p>{}</p>"

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, "version", 0))

        if obj_version != version:
            continue

        res.append(template.format(obj.absolute_url()))

    return "".join(res)


def get_tile_type(tile, from_cover, to_cover):
    """Return tile type"""
    tiles_types = {
        "RichTextWithTitle": "eea.climateadapt.richtext_with_title",
        "EmbedTile": "collective.cover.embed",
        "RichTextTile": "collective.cover.richtext",
        "SearchAceContentTile": "eea.climateadapt.search_acecontent",
        "GenericViewTile": "eea.climateadapt.genericview",
        "RelevantAceContentItemsTile": "eea.climateadapt.relevant_acecontent",
        "ASTNavigationTile": "eea.climateadapt.ast_navigation",
        "ASTHeaderTile": "eea.climateadapt.ast_header",
        "FilterAceContentItemsTile": "eea.climateadapt.filter_acecontent",
        "TransRegionalSelectTile": "eea.climateadapt.transregionselect",
        "SectionNavTile": "eea.climateadapt.section_nav",
        "CountrySelectTile": "eea.climateadapt.countryselect",
        "BannerTile": "collective.cover.banner",
        "ShareInfoTile": "eea.climateadapt.shareinfo",
        "FormTile": "eea.climateadapt.formtile",
        "UrbanMenuTile": "eea.climateadapt.urbanmenu",
        "CardsTile": "eea.climateadapt.cards_tile",
    }
    for a_type in tiles_types.keys():
        if a_type in str(type(tile)):
            return tiles_types[a_type]

    return None


def copy_tiles(tiles, from_cover, to_cover):
    """Copy the tiles from cover to translated cover"""
    logger.info("Copy tiles")
    logger.info(from_cover.absolute_url())
    logger.info(to_cover.absolute_url())
    for tile in tiles:
        tile_type = get_tile_type(tile, from_cover, to_cover)

        if tile_type is not None:
            from_tile = from_cover.restrictedTraverse(
                "@@{0}/{1}".format(tile_type, tile.id)
            )

            to_tile = to_cover.restrictedTraverse(
                "@@{0}/{1}".format(tile_type, tile.id)
            )

            from_data_mgr = ITileDataManager(from_tile)
            to_data_mgr = ITileDataManager(to_tile)
            to_data_mgr.set(from_data_mgr.get())

        else:
            logger.info("Missing tile type")
            import pdb

            pdb.set_trace()


def check_full_path_exists(obj, language):
    """Create full path for a object"""

    parent = aq_parent(aq_inner(obj))
    path = parent.getPhysicalPath()
    if len(path) <= 2:
        return True

    translations = TranslationManager(parent).get_translations()
    if language not in translations:
        # TODO, what if the parent path already exist in language
        # but is not linked in translation manager
        create_translation_object(parent, language)


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


def create_translation_object(obj, language):
    """Create translation object for an obj"""
    if language in TranslationManager(obj).get_translations():
        logger.info("Skip creating translation. Already exists.")
        return

    check_full_path_exists(obj, language)
    factory = DefaultTranslationFactory(obj)

    translated_object = factory(language)

    TranslationManager(obj).register_translation(language, translated_object)

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

    if obj.portal_type == "collective.cover.content":
        tiles = [obj.get_tile(x) for x in obj.list_tiles()]
        translated_object.cover_layout = obj.cover_layout
        copy_tiles(tiles, obj, translated_object)

    copy_missing_interfaces(obj, translated_object)
    translated_object.reindexObject()


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


def execute_trans_script(site, language):
    """Clone the content to be translated"""
    catalog = site.portal_catalog
    english_container = site["en"]
    language_folders = [
        x.id for x in catalog.searchResults(path="/cca", portal_type="LRF")
    ]
    language_folders.remove("en")

    # removed 'frontpage-slides' from lang_independent_objects
    lang_independent_objects = [
        "newsletter",
        "Members",
        "repository",
        "test-baltic",
        "frontpage",
        "admin",
        "more-latest-updates",
        "sandbox",
        "portal_pdf",
        "portal_vocabularies",
        "portal_depiction",
        "dashboard",
        "latest-modifications-on-climate-adapt",
        "covenant-of-mayors-external-website",
        "rss-feed",
        "latest-news-events-on-climate-adapt",
        "specific-privacy-statement-for-climate-adapt",
        "privacy-and-legal-notice",
        "database-items-overview",
        "broken-links",
        "observatory-organisations",
        "observatory-management-group-organisations",
        "indicators-backup",
        "eea-copyright-notice",
        "eea-disclaimer",
        "user-dashboard",
    ]

    # move folders under /en/
    for brain in site.getFolderContents():
        obj = brain.getObject()

        if obj.portal_type != "LRF" and obj.id not in lang_independent_objects:
            content.move(source=obj, target=english_container)

    transaction.commit()
    errors = []
    # get and parse all objects under /en/
    res = get_all_objs(english_container)

    count = 0
    for brain in res:
        logger.info("--------------------------------------------------------")
        logger.info(count)
        count += 1
        if brain.getPath() == "/cca/en" or brain.portal_type == "LIF":
            continue
        obj = brain.getObject()
        try:
            create_translation_object(obj, language)
            logger.info("Cloned: %s" % obj.absolute_url())
        except Exception as err:
            logger.info("Error cloning: %s" % obj.absolute_url())
            if err.message == "Translation already exists":
                continue
            else:
                errors.append(obj)

        if count % 200 == 0:
            logger.info("Processed %s objects" % count)
            transaction.commit()

    transaction.commit()
    logger.info("Errors")
    logger.info(errors)
    logger.info("Finished cloning for language %s" % language)

    return "Finished cloning for language %s" % language


def verify_unlinked_translation(site, request):
    """Clone the content to be translated if not exist"""
    # language = request.get("language", None)
    available_languages = ["es", "de", "it", "pl", "fr"]
    check_nr_languages = request.get(
        "check_nr_languages", len(available_languages) + 1)
    uid = request.get("uid", None)
    # limit = int(request.get("limit", 0))
    # offset = int(request.get("offset", 0))
    portal_type = request.get("portal_type", None)

    # catalog = site.portal_catalog
    language_container = site["en"]

    # get and parse all objects under /en/
    res = get_all_objs(language_container)

    # failed_translations = []
    # count = 0
    for brain in res:
        obj = brain.getObject()

        if uid and uid != brain.UID:
            continue
        if portal_type and portal_type != obj.portal_type:
            continue

        translations = TranslationManager(obj).get_translations()

        if len(translations) < check_nr_languages:
            logger.info(obj.absolute_url())
            for available_language in available_languages:
                create_translation_object(obj, available_language)


def report_unlinked_translation(site, request):
    """Report untranslated items"""
    # language = request.get("language", None)
    available_languages = ["es", "de", "it", "pl", "fr"]
    check_nr_languages = request.get(
        "check_nr_languages", len(available_languages) + 1)
    uid = request.get("uid", None)
    # limit = int(request.get("limit", 0))
    # offset = int(request.get("offset", 0))
    portal_type = request.get("portal_type", None)

    # catalog = site.portal_catalog
    language_container = site["en"]

    res = {}
    # get and parse all objects under /en/
    brains = get_all_objs(language_container)

    count = 0
    report_date = datetime.now().strftime("%Y_%m_%d")

    for brain in brains:
        count += 1
        obj = brain.getObject()

        if uid and uid != brain.UID:
            continue
        if portal_type and portal_type != obj.portal_type:
            continue

        translations = TranslationManager(obj).get_translations()

        if len(translations) < check_nr_languages:
            res[brain.UID] = obj.absolute_url()

    json_object = json.dumps(res, indent=4)
    with open(
        "/tmp/report_unlinked_translation_" + report_date + ".json", "w"
    ) as outfile:
        outfile.write(json_object)

    return res


def admin_some_translated(site, items):
    """Create a list of links to be tested (for translation) for each
    content type
    """
    items = int(items)
    catalog = site.portal_catalog
    portal_types = []
    links = {}
    fields = {}

    res = catalog.searchResults(path="/cca/en")
    count = -1
    for brain in res:
        count += 1
        logger.info(count)
        obj = brain.getObject()

        portal_type = obj.portal_type
        if portal_type not in portal_types:
            portal_types.append(portal_type)
            links[portal_type] = []

            # get behavior fields and values
            behavior_assignable = IBehaviorAssignable(obj)
            _fields = {}
            if behavior_assignable:
                behaviors = behavior_assignable.enumerateBehaviors()
                for behavior in behaviors:
                    for k, val in getFieldsInOrder(behavior.interface):
                        _fields.update({k: val})

            #  get schema fields and values
            for k, val in getFieldsInOrder(obj.getTypeInfo().lookupSchema()):
                _fields.update({k: val})

            fields[portal_type] = [(x, _fields[x]) for x in _fields]

        if len(links[portal_type]) < items:
            links[portal_type].append(obj.absolute_url())

    return {"Content types": portal_types, "Links": links, "fields": fields}


def is_volto_context(context):
    volto_contexts = ['/en/mission', '/en/observatory']
    for value in volto_contexts:
        if value in context.absolute_url():
            return True
    return False


def execute_translate_async(context, options, language, request_vars):
    """translate via zc.async"""
    if options.get('is_volto', None) is not None:
        retrieve_volto_html_translation(
            options['http_host'],
            "en",
            options['html_content'].encode("utf-8"),
            options['trans_obj_path'],
            target_languages=language.upper(),
        )
        return

    if is_volto_context(context):
        logger.info("SKIP classic translation in volto context")
        return

    if not hasattr(context, "REQUEST"):
        zopeUtils._Z2HOST = options["http_host"]
        context = zopeUtils.makerequest(context)
        context.REQUEST.other["SERVER_URL"] = context.REQUEST.other[
            "SERVER_URL"
        ].replace("http", "https")
        # context.REQUEST['PARENTS'] = [context]

        for k, v in request_vars.items():
            context.REQUEST.set(k, v)

    settings = {
        "language": language,
        "uid": options["uid"],
    }

    translation_step_4(context, settings, async_request=True)
    site_portal = portal.get()
    site_portal.REQUEST = context.REQUEST

    translate_obj(context, lang=language, one_step=True)

    # trans_obj = get_translation_object(context, language)
    # copy_missing_interfaces(context, trans_obj)

    # delete REQUEST to avoid pickle error
    # del context.REQUEST
    del site_portal.REQUEST

    logger.info("Async translate for object %s", options["obj_url"])

    # try:
    # except Exception as err:
    #     # async_service = get_async_service()
    #
    #     # re-schedule PING on error
    #     # schedule = datetime.now(pytz.UTC) + timedelta(hours=4)
    #     # queue = async_service.getQueues()['']
    #     # async_service.queueJobInQueueWithDelay(
    #     #     None, schedule, queue, ('translate',),
    #     #     execute_translate_step_4_async, context, options, language, request_vars
    #     # )
    #
    #     # mark the original job as failed
    #     return "Translate rescheduled for object %s. " "Reason: %s " % (
    #         options["obj_url"],
    #         str(err),
    #     )

    return "Finished"
