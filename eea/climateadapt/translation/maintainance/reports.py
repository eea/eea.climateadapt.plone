import json
import logging
from datetime import datetime

from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.value import RichTextValue
from plone.behavior.interfaces import IBehaviorAssignable
from Products.Five.browser import BrowserView
from zope.schema import getFieldsInOrder

from ..admin import is_obj_skipped_for_translation
from ..core import (
    create_translation_object,
    get_all_objs,
)

logger = logging.getLogger("eea.climateadapt")


def verify_unlinked_translation(site, request):
    """Clone the content to be translated if not exist"""
    # language = request.get("language", None)
    available_languages = ["es", "de", "it", "pl", "fr"]
    check_nr_languages = request.get("check_nr_languages", len(available_languages) + 1)
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


class VerifyUnlinkedTranslation(BrowserView):
    """Check items which does not have relation to english
    Usage: /admin-verify-unlinked-translation
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_unlinked_translation(portal.getSite(), self.request)


def report_unlinked_translation(site, request):
    """Report untranslated items"""
    # language = request.get("language", None)
    available_languages = ["es", "de", "it", "pl", "fr"]
    check_nr_languages = request.get("check_nr_languages", len(available_languages) + 1)
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


class ReportUnlinkedTranslation(BrowserView):
    """Check items which does not have relation to english
    Usage: /admin-report-unlinked-translation
    """

    def report(self, **kwargs):
        kwargs.update(self.request.form)
        return report_unlinked_translation(portal.getSite(), self.request)


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


class VerifyClonedLanguage(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-verify-cloned?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_cloned_language(portal.getSite(), **kwargs)


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


class VerifyTranslationFields(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-verify-translation-fields?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return verify_translation_fields(portal.getSite(), self.request)
