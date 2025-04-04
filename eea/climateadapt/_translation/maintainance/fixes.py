import logging
from plone.app.multilingual.manager import TranslationManager
import json

from plone.api import portal
from Products.Five.browser import BrowserView

from ..utils import is_json
from .steps import translation_step_2


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


class TranslateRepaire(BrowserView):
    """Use this view to save the values from annotation in objects fields

    Usage: /admin-translate-repaire?language=es&file=ABCDEF
    file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire(portal.getSite(), self.request)


def translation_repaire_step_3(site, request):
    """Get all jsons objects in english and overwrite targeted language
    object with translations.
    """
    print((site, request))
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


class TranslateRepaireStep3(BrowserView):
    """Use this view to save the values from annotation in objects fields

    Usage: /admin-translate-repaire-step-3?language=es&file=ABCDEF
    file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire_step_3(portal.getSite(), self.request)


logger = logging.getLogger("eea.climateadapt")


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
                        trans_obj.aq_parent.manage_renameObject(trans_obj.id, obj.id)
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
                logger.info("NOT SOLVED. Missing translation: %s", trans_obj_path)
                not_solved["missing_translation"].append(obj_url)

    logger.info("DONE. Solved: %s", solved)
    logger.info("Not solved:")
    logger.info(not_solved)
    return {"solved": solved, "not_solved": not_solved}


class FixUrlsForTranslatedContent(BrowserView):
    """Use this view to check all links for a new cloned language
    Usage: /admin-fix-urls-translated-content?language=ro
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return fix_urls_for_translated_content(portal.getSite(), **kwargs)
