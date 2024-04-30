"""Translation views"""

import base64
import cgi
import logging
import os

from eea.climateadapt.browser.admin import force_unlock
from eea.climateadapt.translation.volto import (
    get_content_from_html,
    translate_volto_html,
)
from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter

from . import (
    get_translation_key_values,
    get_translation_keys,
    get_translation_report,
)
from .core import (
    copy_missing_interfaces,
    handle_cover_step_4,
    handle_folder_doc_step_4,
    handle_link,
    save_field_data,
)

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get


class TranslationCallback(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations (or directly in the object in case
    of html fields).
    """

    def __call__(self):
        # for some reason this request acts strange
        qs = self.request["QUERY_STRING"]
        parsed = cgi.parse_qs(qs)
        form = {}
        for name, val in parsed.items():
            form[name] = val[0]

        _file = self.request._file.read()
        logger.info("Translation Callback Incoming form: %s" % form)
        logger.info("Translation Callback Incoming file: %s" % _file)

        self.save_html_volto(form, _file)
        return "ok"

    def save_html_volto(self, form, b64_str):
        # file.seek(0)
        # b64_str = file.read()
        html_translated = base64.decodestring(b64_str).decode("latin-1")

        logger.info("Translate volto html form: %s", form)
        logger.info("Translate volto html: %s", html_translated)

        site = portal.getSite()
        trans_obj_path = form.get("external-reference")
        if "https://" in trans_obj_path:
            trans_obj_path = "/cca" + trans_obj_path.split(site.absolute_url())[-1]

        trans_obj = site.unrestrictedTraverse(trans_obj_path)
        force_unlock(trans_obj)

        fielddata = get_content_from_html(html_translated.encode("latin-1"))

        translations = TranslationManager(trans_obj).get_translations()
        en_obj = translations["en"]  # hardcoded, should use canonical

        save_field_data(en_obj, trans_obj, fielddata)

        copy_missing_interfaces(en_obj, trans_obj)

        # layout_en = en_obj.getLayout()
        # if layout_en:
        #     trans_obj.setLayout(layout_en)

        if trans_obj.portal_type == "collective.cover.content":
            handle_cover_step_4(en_obj, trans_obj, trans_obj.language, False)
        if trans_obj.portal_type in ("Folder", "Document"):
            handle_folder_doc_step_4(en_obj, trans_obj, False, False)
        if trans_obj.portal_type in ["Link"]:
            handle_link(en_obj, trans_obj)

        # TODO: sync workflow state

        trans_obj._p_changed = True
        trans_obj.reindexObject()
        logger.info("Html volto translation saved for %s", trans_obj.absolute_url())


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj = self.context
        html = getMultiAdapter((self.context, self.context.REQUEST), name="tohtml")()
        site = portal.getSite()
        http_host = self.context.REQUEST.environ.get(
            "HTTP_X_FORWARDED_HOST", site.absolute_url()
        )

        translate_volto_html(html, obj, http_host)

        self.request.response.redirect(obj.absolute_url())


class TranslationList(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations

    Used with multiple templates, registered as /@@translate-list, /@@translate-report, /@@translate-key

    TODO: remove this, no longer needed
    """

    def list(self):
        form = self.request.form
        search = form.get("search", None)
        limit = int(form.get("limit", 10))

        data = get_translation_keys()
        if search:
            data = [item for item in data if search in item]
        if len(data) > limit:
            data = data[0:limit]
        return data

    def keys(self):
        key = self.request.form["key"]
        return get_translation_key_values(key)

    def report(self):
        return get_translation_report()


# form = self.request.form
#
# if form.get("is_volto", None) is not None:
#     file = self.request.stdin
#     return
#
# # NOTE:: the code below is no longer used, we only use the above method
#
# if form.get("format", None) == "html":
#     file = self.request.stdin
#     self.save_html_fields(form, file)
#     logger.info("Translate html")
#     return
#
# if (
#     form.get("one_step", None) == "true"
#     and form.get("is_cover", None) != "true"
# ):
#     uid = form.get("uid", None)
#     trans_obj_path = form.get("external-reference")
#     if "https://" in trans_obj_path:
#         site = portal.getSite()
#         trans_obj_path = "/cca" + \
#             trans_obj_path.split(site.absolute_url())[-1]
#     field = form.get("field", None)
#     if uid is not None and field is not None:
#         form.pop("uid", None)
#         form.pop("one_step", None)
#         form.pop("request-id", None)
#         form.pop("external-reference", None)
#         form.pop("target-language", None)
#         form.pop("field", None)
#         form.pop("source_lang", None)
#
#         if len(form.keys()) > 1 and "\n" in form:
#             # This was the case of
#             # /cca/de/eu-adaptation-policy/sector-policies/forestry/index_html
#             # where eTranslation added a new key in the form
#             # and this happened only for DE, resulting a single
#             # not translated title
#             # https://taskman.eionet.europa.eu/issues/155311#note-38
#             form.pop("\n", None)
#
#         translated = form.pop("translation", form.keys()[0]).strip()
#         translated = translated.decode("latin-1")
#         self.save_text_field(uid, field, translated, trans_obj_path)
#     else:
#         logger.info("Wrong callback data. Missing uid or field name.")
#     return
#
# if (
#     form.get("one_step", None) == "true"
#     and form.get("is_cover", None) == "true"
# ):
#     self.save_tile_field(form)
#     return
#
# deps = ["translation"]
# event.notify(InvalidateMemCacheEvent(raw=True, dependencies=deps))
# logger.info("Invalidate cache for dependencies: %s", ", ".join(deps))
#
# logger.info("Translate params all : %r", form)
#
# form.pop("request-id", None)
# target_language = form.pop("target-language", None)
#
# language = form.pop("source_lang", None)
#
# if language is None:
#     language = ITranslationContext(self.context).language
#
# original = form.pop("external-reference", "")
# original = normalize(original)
#
# logger.info("Translate params all : %r", form)
#
# translated = form.pop("translation", form.keys()[0]).strip()
#
# # translated = decode_text(translated)
# # it seems the EC service sends translated text in latin-1.
# # Please double-check, but the decode_text that automatically detects
# # the encoding doesn't seem to do a great job
#
# translated = translated.decode("latin-1")
#
# save_translation(original, translated, language, target_language)
#
# return (
#     '<a href="/@@translate-key?key=' + original + '">available translations</a>'
# )
#
# def save_tile_field(self, form):
#     """Save a simple text filed in a cover tile"""
#     field = form.get("field", None)
#     tile_id = form.get("tile_id", None)
#     if tile_id is not None and field is not None:
#         form.pop("uid", None)
#         form.pop("one_step", None)
#         form.pop("request-id", None)
#         trans_obj_path = form.get("external-reference")
#         form.pop("external-reference", None)
#         form.pop("target-language", None)
#         form.pop("field", None)
#         form.pop("source_lang", None)
#         form.pop("tile_id", None)
#         form.pop("is_cover", None)
#         translated = form.pop("translation", form.keys()[0]).strip()
#         # translated = translated.decode('latin-1')
#
#         tile_annot_id = "plone.tiles.data." + tile_id
#         site = portal.getSite()
#         if "https://" in trans_obj_path:
#             trans_obj_path = "/cca" + \
#                 trans_obj_path.split(site.absolute_url())[-1]
#         trans_obj = site.unrestrictedTraverse(trans_obj_path)
#         tile = trans_obj.__annotations__.get(tile_annot_id, None)
#
#         if not tile:
#             return
#
#         try:
#             update = tile.data
#         except AttributeError:
#             update = tile
#
#         translated_msg = translated
#         if translated_msg is not None:
#             update[field] = translated_msg
#
#         try:
#             trans_obj.__annotations__[tile_annot_id] = update
#         except Exception:
#             logger.info("One step: Error on saving translated tile field")
#             # import pdb; pdb.set_trace()

# def save_text_field(self, uid, field, value, trans_obj_path):
#     """Save the translated value of given field for specified obj by uid"""
#     site = portal.getSite()
#     # catalog = site.portal_catalog
#     # trans_obj = get_translation_object_from_uid(uid, catalog)
#     trans_obj = site.unrestrictedTraverse(trans_obj_path)
#
#     if value is not None and value != "":
#         force_unlock(trans_obj)
#         encoded_text = value.encode("latin-1")
#         have_change = False
#
#         try:
#             setattr(trans_obj, field, encoded_text)
#             have_change = True
#         except AttributeError:
#             logger.info(
#                 "One step: AttributeError for obj: %s key: %s",
#                 trans_obj.absolute_url(),
#                 field,
#             )
#
#         if have_change:
#             trans_obj._p_changed = True
#             trans_obj.reindexObject()
#
#         logger.info("One step: saved %s %s %s", uid, field, value)

# def save_html_fields(self, form, file):
#     """Get the translated html file, extract the values for each field and
#     update the related translation object.
#     """
#     site = portal.getSite()
#     trans_obj_path = form.get("external-reference")
#     if "https://" in trans_obj_path:
#         trans_obj_path = "/cca" + \
#             trans_obj_path.split(site.absolute_url())[-1]
#
#     form.pop("format")
#     form.pop("request-id")
#     form.pop("external-reference")
#     form.pop("source_lang")
#     form.pop("target-language")
#
#     # source_lang = form.get("source_lang")
#     # target_lang = form.get("target-language")
#     # logger.info("Translate %s to %s", source_lang, target_lang)
#
#     trans_obj = site.unrestrictedTraverse(trans_obj_path)
#     force_unlock(trans_obj)
#
#     if len(form.keys()) == 0:
#         logger.info("Empty form")  # TODO: Check why?
#         return
#
#     file.seek(0)
#     b64_str = file.read()
#     html_file = base64.decodestring(b64_str).decode("latin-1")
#     # logger.info(html_file)
#     # soup = BeautifulSoup(html_file, "html.parser")
#     soup = BeautifulSoup(html_file, "lxml")  # it's seems better
#     # for invalid HTML cases.
#
#     html_fields = soup.find_all(
#         "div", attrs={"class": "cca-translation-section"})
#
#     for field in html_fields:
#         field_name = field["data-field"]
#         html_value = field.decode_contents()
#         encoded_text = html_value.encode("latin-1")
#         setattr(trans_obj, field_name, RichTextValue(encoded_text))
#         trans_obj._p_changed = True
#         trans_obj.reindexObject(idxs=[field_name])
#
#     tiles = soup.find_all("div", attrs={"class": "cca-translation-tile"})
#
#     for field in tiles:
#         field_name = field["data-field"]
#         tile_id = field["data-tile-id"]
#         html_value = field.decode_contents()
#         encoded_text = html_value.encode("latin-1")
#         # tile = trans_obj.get_tile(tile_id)
#         tile_annot_id = "plone.tiles.data." + tile_id
#         tile = trans_obj.__annotations__.get(tile_annot_id, None)
#         if tile is not None:
#             try:
#                 update = tile.data
#             except AttributeError:
#                 update = tile
#             update["text"] = RichTextValue(encoded_text)
#             # tile.data.update(update)
#             trans_obj.__annotations__[tile_annot_id] = update
#             # trans_obj.reindexObject()
#         else:
#             logger.info("Cannot find tile")
#     logger.info("Html translation saved for %s", trans_obj.absolute_url())
# from eea.cache.event import InvalidateMemCacheEvent
# from zope import event
# from .interfaces import ITranslationContext
# from bs4 import BeautifulSoup
# from plone.app.textfield.value import RichTextValue
# normalize,
# save_translation,
