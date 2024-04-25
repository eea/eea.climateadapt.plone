"""Admin translation"""

import json
import logging
from collections import defaultdict

from Products.Five.browser import BrowserView
from zope.site.hooks import getSite

from eea.climateadapt import CcaAdminMessageFactory as _

from .core import (
    is_obj_skipped_for_translation,
)
from .utils import get_object_fields_values

# copy_missing_interfaces,
# create_translation_object,
# translate_obj,
# trans_copy_field_data,


# from eea.climateadapt.translation.utils import (
#     get_site_languages,
# )
# import transaction
# from plone import api
# from plone.app.multilingual.manager import TranslationManager
# from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone import utils
# from Products.statusmessages.interfaces import IStatusMessage
# from zope.globalrequest import getRequest

logger = logging.getLogger("eea.climateadapt")


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


class TranslationListTypeFields(BrowserView):
    """Use this view to translate all json files to a language

    Usage: /admin-translate-step-2?language=ro
    """

    def __call__(self):
        return translation_list_type_fields(getSite())


# class RunTranslationSingleItem(BrowserView):
#     """Translate a single item
#
#     To be used for testing translation without waiting for all objects to
#     be updated
#
#     Usage: item/admin-translate-this
#     """
#
#     def __call__(self):
#         obj = self.context
#         result = translate_obj(obj)
#         # transaction.commit()
#         return result


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


class TranslationStatus(BrowserView):
    """Display the the current versions for all translated objects"""

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)

        if "version" in kwargs:
            return translations_status_by_version(getSite(), **kwargs)

        return translations_status(getSite(), **kwargs)


# class TranslateOneObject(BrowserView):
#     """Translate one object."""
#
#     def translate(self):
#         response = {"error": None, "items": [], "url": None}
#         request = getRequest()
#         url = request.get("url", None)
#         response["url"] = url
#         if url:
#             site = api.portal.get()
#             try:
#                 obj = site.unrestrictedTraverse("/cca" + url)
#             except Exception:
#                 response["error"] = "NOT FOUND"
#                 return response
#
#             if "/en/" in obj.absolute_url():
#                 response["items"] = self.create_translations(obj)
#                 self.translate_obj(obj)
#                 # self.set_workflow_states(obj)
#
#                 self.copy_interfaces(obj)  # TODO: delete. It's included in
#                 # create_translation_object. It is used here only for testing
#                 # on old created content. Example: fixing interfaces for pages
#                 # like share-your-info
#
#                 self.copy_fields(obj)
#             else:
#                 response["error"] = "/en/ not found in url"
#         return response
#
#     def get_url(self):
#         return self.request.form["url"]
#
#     def error(self, obj, error):
#         request = getattr(self.context, "REQUEST", None)
#         if request is not None:
#             title = utils.pretty_title_or_id(obj, obj)
#             message = _(
#                 "Unable to translate ${name} as part of content rule "
#                 "'translate' action: ${error}",
#                 mapping={"name": title, "error": error},
#             )
#             IStatusMessage(request).addStatusMessage(message, type="error")
#
#     def create_translations(self, obj):
#         response = []
#         """ Make sure all translations (cloned) objs exists for this obj
#         """
#         transaction.savepoint()
#         translations = TranslationManager(obj).get_translations()
#         for language in get_site_languages():
#             if language != "en" and language not in translations:
#                 try:
#                     create_translation_object(obj, language)
#                 except Exception:
#                     pass
#             if language != "en":
#                 response.append(obj.absolute_url())
#         transaction.commit()
#         return response
#
#     def translate_obj(self, obj):
#         """Send the obj to be translated"""
#         try:
#             translate_obj(obj, one_step=True)
#         except Exception as e:
#             self.error(obj, str(e))
#
#     def copy_interfaces(self, obj):
#         """Copy interfaces from en to translated obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             trans_obj = translations[language]
#             copy_missing_interfaces(obj, trans_obj)
#
#     def set_workflow_states(self, obj):
#         """Mark translations as not approved"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             this_obj = translations[language]
#             wftool = getToolByName(this_obj, "portal_workflow")
#             wftool.doActionFor(this_obj, "send_to_translation_not_approved")
#
#     def copy_fields(self, obj):
#         """Run step 4 for this obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             if language != "en":
#                 settings = {
#                     "language": language,
#                     "uid": obj.UID(),
#                 }
#                 trans_copy_field_data(getSite(), settings)


# @adapter(Interface, ITranslateAction, Interface)
# @implementer(IExecutable)
