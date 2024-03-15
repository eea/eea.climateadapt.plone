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


class TranslateRepaireStep3(BrowserView):
    """Use this view to save the values from annotation in objects fields

    Usage: /admin-translate-repaire-step-3?language=es&file=ABCDEF
    file : /tmp/[ABCDEF].json
    """

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)
        return translation_repaire_step_3(portal.getSite(), self.request)
