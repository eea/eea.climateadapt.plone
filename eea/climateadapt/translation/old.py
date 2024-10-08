# from plone.app.uuid.utils import uuidToObject
# from plone.tiles.interfaces import ITileDataManager
# from plone.uuid.interfaces import IUUID
from . import get_translation_key_values, get_translation_keys, get_translation_report

# __import__('pdb').set_trace()
if data.get("cover_layout"):
     frags = fragments_fromstring(data["cover_layout"])
      tiles = {}
       for frag in frags:
            # <div data-tile-id=".b3898bdb-017c-4dac-a2d4-556d59d0ea6d"><div data-tile-field="text">
            id = frag.get("data-tile-id")
            info = {}

            for child in frag:
                fieldname = child.get("data-tile-field")
                isrichtext = child.get("data-tile-type") == "richtext"
                if isrichtext:
                    info[fieldname] = elements_to_text(child)
                else:
                    info[fieldname] = child.text
            tiles[id] = info

        data["cover_layout"] = tiles


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


# from copy import deepcopy
# def copy_tiles_to_translation(en_obj, trans_obj, site_portal):
#     trans_obj_path = "/".join(trans_obj.getPhysicalPath())
#     trans_obj = wrap_in_aquisition(trans_obj_path, site_portal)
#     tiles = [en_obj.get_tile(x) for x in en_obj.list_tiles()]
#     trans_obj.cover_layout = en_obj.cover_layout
#     copy_tiles(tiles, en_obj, trans_obj)


# cover_fixes = {"eea.climateadapt.cards_tile": fix_cards_tile}

# def handle_cover_step_4(obj, trans_obj, language, reindex):
#     """Used by save_html_volto. Adapts the cover data from one cover to another"""
#
#     data_tiles = obj.get_tiles()
#
#     for data_tile in data_tiles:
#         if data_tile["type"] == "eea.climateadapt.cards_tile":
#             data_trans_tiles = obj.get_tiles()
#             for data_trans_tile in data_trans_tiles:
#                 fixer = cover_fixes.get(data_trans_tile["type"], None)
#                 if fixer:
#                     fixer(obj, trans_obj, data_tile, data_trans_tile, language)
#
#         if data_tile["type"] == "eea.climateadapt.relevant_acecontent":
#             tile_id = data_tile["id"]
#             plone_tile_id = "plone.tiles.data" + tile_id
#             trans_tile = trans_obj.__annotations__.get(plone_tile_id) or {}
#             saved_title = trans_tile.get("title")
#
#             from_data = obj.__annotations__.get(plone_tile_id, None)
#             if from_data:
#                 data = deepcopy(from_data)
#                 if saved_title:
#                     data["title"] = saved_title
#
#                 trans_obj.__annotations__[plone_tile_id] = data
#
#     force_unlock(obj)
#     layout_en = obj.getLayout()
#     if layout_en:
#         reindex = True
#         trans_obj.setLayout(layout_en)
#
#     return reindex

# def get_tile_type(tile, from_cover, to_cover):
#     """Return tile type"""
#     tiles_types = {
#         "RichTextWithTitle": "eea.climateadapt.richtext_with_title",
#         "EmbedTile": "collective.cover.embed",
#         "RichTextTile": "collective.cover.richtext",
#         "SearchAceContentTile": "eea.climateadapt.search_acecontent",
#         "GenericViewTile": "eea.climateadapt.genericview",
#         "RelevantAceContentItemsTile": "eea.climateadapt.relevant_acecontent",
#         "ASTNavigationTile": "eea.climateadapt.ast_navigation",
#         "ASTHeaderTile": "eea.climateadapt.ast_header",
#         "FilterAceContentItemsTile": "eea.climateadapt.filter_acecontent",
#         "TransRegionalSelectTile": "eea.climateadapt.transregionselect",
#         "SectionNavTile": "eea.climateadapt.section_nav",
#         "CountrySelectTile": "eea.climateadapt.countryselect",
#         "BannerTile": "collective.cover.banner",
#         "ShareInfoTile": "eea.climateadapt.shareinfo",
#         "FormTile": "eea.climateadapt.formtile",
#         "UrbanMenuTile": "eea.climateadapt.urbanmenu",
#         "CardsTile": "eea.climateadapt.cards_tile",
#     }
#     for a_type in tiles_types.keys():
#         if a_type in str(type(tile)):
#             return tiles_types[a_type]
#
#     return None

# def copy_tiles(tiles, from_cover, to_cover):
#     """Copy the tiles from cover to translated cover"""
#     logger.info("Copy tiles from cover: %s", from_cover.absolute_url())
#     logger.info("Copy tiles to cover: %s", to_cover.absolute_url())
#
#     for tile in tiles:
#         tile_type = get_tile_type(tile, from_cover, to_cover)
#
#         if tile_type is not None:
#             from_tile = from_cover.restrictedTraverse(
#                 "@@{0}/{1}".format(tile_type, tile.id)
#             )
#
#             to_tile = to_cover.restrictedTraverse(
#                 "@@{0}/{1}".format(tile_type, tile.id)
#             )
#
#             from_data_mgr = ITileDataManager(from_tile)
#             to_data_mgr = ITileDataManager(to_tile)
#             to_data_mgr.set(from_data_mgr.get())
#
#         else:
#             logger.info("Missing tile type")
#             # import pdb
#             #
#             # pdb.set_trace()


# if "cover_layout" in fielddata:
#     coverdata = fielddata["cover_layout"]
#
#     for tileid in coverdata.keys():
#         full_tile_id = "plone.tiles.data.%s" % tileid
#
#         # tile is missing in the translation, so we may copy it from the original
#         tile = trans_obj.__annotations__.get(full_tile_id)
#         if tile is None:
#             tile = canonical.__annotations__.get(full_tile_id, None)
#             if tile is None:
#                 logger.warning(
#                     "Tile is missing from both the original and the translation: %s / %s",
#                     full_tile_id,
#                     trans_obj.absolute_url(),
#                 )
#                 continue
#             tile = deepcopy(tile)
#
#         for fieldname, fieldvalue in coverdata[tileid].items():
#             orig = tile[fieldname]
#             if isinstance(orig, RichTextValue):
#                 tile[fieldname] = RichTextValue(fieldvalue)
#             else:
#                 tile[fieldname] = fieldvalue
#         trans_obj.__annotations__["plone.tiles.data.%s" % tileid] = tile
#
#     trans_obj.__annotations__._p_changed = True
# from lxml.html import builder as E
# from lxml.html import fragments_fromstring, tostring
# create_translation_object,
# def convert_richtext_to_fragments(mayberichtextvalue):
#     if mayberichtextvalue and mayberichtextvalue.raw:
#         return fragments_fromstring(mayberichtextvalue.raw)
#     return []
# def get_cover_as_html(obj):
#     elements = []
#     unwrapped = obj.aq_inner.aq_self
#     annot = getattr(unwrapped, "__annotations__", None)
#     m = "plone.tiles.data"
#
#     if annot:
#         for k in annot.keys():
#             if k.startswith(m):
#                 attribs = {"data-tile-id": k[len(m) + 1 :]}
#                 children = []
#                 data = annot[k]
#                 if data.get("title"):
#                     title = data.get("title")
#                     if not isinstance(title, unicode):
#                         title = title.decode("utf-8")
#                     try:
#                         d = {"data-tile-field": "title"}
#                         children.append(E.DIV(title, **d))
#                     except:
#                         __traceback_info__ = ("Wrong value for XML", str(title))
#
#                 if data.get("text"):
#                     frags = convert_richtext_to_fragments(data["text"])
#                     d = {"data-tile-field": "text", "data-tile-type": "richtext"}
#                     children.append(E.DIV(*frags, **d))
#
#                 div = E.DIV(*children, **attribs)
#                 elements.append(div)
#
#     return elements_to_text(elements)
def fix_cards_tile(obj, trans_obj, data_tile, data_trans_tile, language):
    # We link the collection tile to the translated version
    tile = obj.get_tile(data_tile["id"])
    try:
        trans_tile = trans_obj.get_tile(data_trans_tile["id"])
    except ValueError:
        logger.info("Tile not found.")
        trans_tile = None

    if trans_tile is not None:
        collection_obj = uuidToObject(tile.data["uuid"])
        collection_trans_obj = get_translation_object(collection_obj, language)

        dataManager = ITileDataManager(trans_tile)

        temp = dataManager.get()
        try:
            temp["uuid"] = IUUID(collection_trans_obj)
        except TypeError:
            logger.info("Collection not found.")

        dataManager.set(temp)
# def execute_translate_step_4_async(context, options, language, request_vars):
#     """translate via zc.async"""
#     if not hasattr(context, "REQUEST"):
#         zopeUtils._Z2HOST = options["obj_url"]
#         context = zopeUtils.makerequest(context)
#         context.REQUEST["PARENTS"] = [context]
#
#         for k, v in request_vars:
#             context.REQUEST.set(k, v)
#
#     try:
#         settings = {
#             "language": language,
#             "uid": options["uid"],
#         }
#         res = trans_copy_field_data(context, settings, async_request=True)
#         logger.info("Async translate for object %s", options["obj_url"])
#
#     except Exception as err:
#         # async_service = get_async_service()
#
#         # re-schedule PING on error
#         # schedule = datetime.now(pytz.UTC) + timedelta(hours=4)
#         # queue = async_service.getQueues()['']
#         # async_service.queueJobInQueueWithDelay(
#         #     None, schedule, queue, ('translate',),
#         #     execute_translate_step_4_async, context, options, language, request_vars
#         # )
#
#         # mark the original job as failed
#         return "Translate rescheduled for object %s. " "Reason: %s " % (
#             options["obj_url"],
#             str(err),
#         )
#
#     return res

# from eea.climateadapt.translation.utils import get_site_languages
# from zope.site.hooks import getSite
# from eea.climateadapt.translation.core import (
#     # copy_missing_interfaces,
#     # create_translation_object,
#     # translate_obj,
#     # trans_copy_field_data,
#     # trans_sync_workflow_state,
# )

# @adapter(Interface, ITranslateAction, Interface)
# @implementer(IExecutable)
# class TranslateActionExecutor(object):
#     """The executor for this action."""
#
#     def __init__(self, context, element, event):
#         self.context = context
#         self.element = element
#         self.event = event
#
#     def __call__(self):
#         obj = self.event.object
#         if "/en/" in obj.absolute_url():
#             self.create_translations(obj)
#             self.copy_fields(obj)
#             self.translate_obj(obj)
#             self.publish_translations(obj)
#             self.copy_interfaces(obj)  # TODO: delete. It's already included in
#
#             # create_translation_object. It is used here only for testing
#             # on old created content. Example: fixing interfaces for pages
#             # like share-your-info
#
#     def error(self, obj, error):
#         """Show error"""
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
#         """Make sure all translations (cloned) objs exists for this obj"""
#         transaction.savepoint()
#         translations = TranslationManager(obj).get_translations()
#
#         for language in get_site_languages():
#             if language != "en" and language not in translations:
#                 create_translation_object(obj, language)
#
#         transaction.commit()
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
#
#     def publish_translations(self, obj):
#         """Run step 5 for this obj"""
#         translations = TranslationManager(obj).get_translations()
#         for language in translations:
#             if language != "en":
#                 settings = {
#                     "language": language,
#                     "uid": obj.UID(),
#                 }
#                 trans_sync_workflow_state(getSite(), settings)


# def retrieve_html_translation(source_lang, html, obj_path, target_languages=None):
#     """Send a call to automatic translation service, to translate a string
#     Returns a json formatted string
#
#     This is not used anymore
#     """
#     if not html:
#         return
#
#     if not target_languages:
#         target_languages = ["EN"]
#
#     encoded_html = base64.b64encode(html)
#
#     site_url = portal.get().absolute_url()
#
#     if "localhost" in site_url:
#         logger.warning(
#             "Using localhost, won't retrieve translation for: %s", html)
#
#     client = Client(
#         "https://webgate.ec.europa.eu/etranslation/si/WSEndpointHandlerService?WSDL",
#         wsse=UsernameToken(TRANS_USERNAME, MARINE_PASS),
#     )
#
#     dest = "{}/@@translate-callback?source_lang={}&format=html".format(
#         site_url, source_lang
#     )
#
#     resp = client.service.translate(
#         {
#             "priority": "5",
#             "external-reference": obj_path,
#             "caller-information": {
#                 "application": "Marine_EEA_20180706",
#                 "username": TRANS_USERNAME,
#             },
#             "document-to-translate-base64": {
#                 "content": encoded_html,
#                 "format": "html",
#                 "fileName": "out",
#             },
#             "source-language": source_lang,
#             "target-languages": {"target-language": target_languages},
#             "domain": "GEN",
#             "output-format": "html",
#             "destinations": {
#                 "http-destination": dest,
#             },
#         }
#     )
#
#     logger.info("Data translation request : html content")
#     logger.info("Response from translation request: %r", resp)
#
#     # if str(resp[0]) == '-':
#     #     # If the response is a negative number this means error. Error codes:
#     #     # https://ec.europa.eu/cefdigital/wiki/display/CEFDIGITAL/How+to+submit+a+translation+request+via+the+CEF+eTranslation+webservice
#     #     import pdb; pdb.set_trace()
#
#     res = {"transId": resp, "externalRefId": html}
#
#     return res


# def translate_one_text_to_translation_storage(
#     country_code, text, target_languages=None, force=False
# ):
#     """Send a call to automatic translation service, to translate a string
#     Returns a json formatted string
#     """
#
#     country_code = _get_country_code(country_code, text)
#
#     if not text:
#         return {}
#
#     if not target_languages:
#         target_languages = ["EN"]
#
#     translation = get_translated(text, target_languages[0])
#
#     if translation:
#         if not (force == "True" or ("...." in translation)):
#             # don't translate already translated strings, it overrides the
#             # translation
#             res = {"transId": translation,
#                    "externalRefId": text, "translated": True}
#             logger.info("Data translation cached : %r", res)
#             return res
#
#     site_url = portal.get().absolute_url()
#
#     if "localhost" in site_url:
#         logger.warning(
#             "Using localhost, won't retrieve translation for: %s", text)
#
#         # return {}
#
#     # if detected language is english skip translation
#
#     # if get_detected_lang(text) == 'en':
#     #     logger.info(
#     #         "English language detected, won't retrive translation for: %s",
#     #         text
#     #     )
#     #
#     #     return
#
#     dest = "{}/@@translate-callback?source_lang={}".format(
#         site_url, country_code)
#
#     # logger.info('Translate callback URL: %s', dest)
#
#     data = {
#         "priority": 5,
#         "callerInformation": {
#             "application": "Marine_EEA_20180706",
#             "username": TRANS_USERNAME,
#         },
#         "domain": "SPD",
#         "externalReference": text,  # externalReference,
#         "textToTranslate": text,
#         "sourceLanguage": country_code,
#         "targetLanguages": target_languages,
#         "destinations": {
#             "httpDestinations": [dest],
#         },
#     }
#
#     logger.info("Data translation request : %r", data)
#
#     resp = requests.post(
#         SERVICE_URL,
#         auth=HTTPDigestAuth("Marine_EEA_20180706", MARINE_PASS),
#         data=json.dumps(data),
#         headers={"Content-Type": "application/json"},
#     )
#     logger.info("Response from translation request: %r", resp.content)
#
#     res = {"transId": resp.content, "externalRefId": text}
#
#     return res


# def translate_one_field_in_one_step(
#     country_code,
#     text,
#     target_languages=None,
#     uid=None,
#     obj_path=None,
#     field=None,
#     tile_data=None,
#     tile_id=None,
# ):
#     """Translate simple text fields in one step.
#
#     Send a call to automatic translation service, to translate a string
#     Returns a json formatted string
#
#     The result will be automatically saved to specified obj and field
#     on callback, without using annotations.
#     """
#
#     if not text:
#         return
#
#     country_code = _get_country_code(country_code, text)
#     site_url = portal.get().absolute_url()
#
#     dest = ""
#
#     is_cover = False
#     if tile_data is not None:
#         dest = "{}/@@translate-callback?one_step=true&source_lang={}&uid={}&field={}&is_cover=true&tile_id={}".format(
#             site_url, country_code, uid, field, tile_id
#         )
#         is_cover = True
#
#     if not target_languages:
#         target_languages = ["EN"]
#
#     if "localhost" in site_url:
#         logger.warning(
#             "Using localhost, won't retrieve translation for: %s", text)
#
#     if is_cover is False:
#         dest = "{}/@@translate-callback?one_step=true&source_lang={}&uid={}&field={}".format(
#             site_url, country_code, uid, field
#         )
#     data = {
#         "priority": 5,
#         "callerInformation": {
#             "application": "Marine_EEA_20180706",
#             "username": TRANS_USERNAME,
#         },
#         "domain": "SPD",
#         "externalReference": obj_path,
#         "textToTranslate": text,
#         "sourceLanguage": country_code,
#         "targetLanguages": target_languages,
#         "destinations": {
#             "httpDestinations": [dest],
#         },
#     }
#
#     logger.info("One step translation request : %r", data)
#
#     resp = requests.post(
#         SERVICE_URL,
#         auth=HTTPDigestAuth("Marine_EEA_20180706", MARINE_PASS),
#         data=json.dumps(data),
#         headers={"Content-Type": "application/json"},
#     )
#     logger.info("One step: resp from translation request: %r", resp.content)
#
#     res = {"transId": resp.content, "externalRefId": text}
#
#     return res


def get_translation_keys(site=None):
    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)

    return list(storage.keys())


def get_translation_report(site=None):
    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)
    report = {"nr_keys": len(storage.keys()), "items": {}}
    data = storage.keys()
    for i in range(len(data)):
        storage_key = storage.get(data[i])
        languages = set(storage_key.keys())
        for language in languages:
            if language not in report["items"]:
                report["items"][language] = 0
            report["items"][language] += 1

    return report

def get_translated(value, language, site=None):
    language = _get_country_code(language, value)

    if site is None:
        site = portal.get()

    storage = ITranslationsStorage(site)

    translated = storage.get(value, {}).get(language, None)

    if translated:
        if hasattr(translated, "text"):
            return translated.text.lstrip("?")

        return translated.lstrip("?")

def get_translation_key_values(key, site=None):
    if site is None:
        site = portal.get()

    res = []
    storage = ITranslationsStorage(site)
    storage_key = storage.get(key, None)
    if storage_key:
        languages = set(storage_key.keys())
        for language in languages:
            res.append(
                {"language": language,
                    "translation": storage_key.get(language, None)}
            )
    return res
def delete_translation(text, source_lang):
    source_lang = _get_country_code(source_lang, text)

    site = portal.get()

    storage = ITranslationsStorage(site)

    if storage.get(source_lang, None):
        decoded = normalize(text)

        if text in storage[source_lang]:
            del storage[source_lang][text]

        if decoded in storage[source_lang]:
            del storage[source_lang][decoded]

            # I don't think this is needed
            storage[source_lang]._p_changed = True
            transaction.commit()
#
# def save_translation(original, translated, source_lang, target_lang, approved=False):
#     source_lang = _get_country_code(source_lang, original)
#
#     logger.info(
#         "Translate callback save: %s :: %s :: %s :: %s",
#         original,
#         translated,
#         source_lang,
#         target_lang,
#     )
#     site = portal.get()
#
#     storage = ITranslationsStorage(site)
#
#     storage_original = storage.get(original, None)
#
#     if storage_original is None:
#         storage_original = OOBTree()
#         storage[original] = storage_original
#
#     translated = Translation(translated)
#     storage_original[target_lang] = translated
#
#     logger.info("Saving to annotation: %s", translated)
def _get_country_code(country_code, text):
    if country_code in TRANS_LANGUAGE_MAPPING:
        country_code = get_mapped_language(country_code, text)

    if country_code in ALTERNATE_COUNTRY_CODES:
        country_code = ALTERNATE_COUNTRY_CODES.get(country_code, country_code)

    return country_code

def decode_text(text):
    encoding = chardet.detect(text)["encoding"]
    text_encoded = text.decode(encoding)

    # import unicodedata
    # text_encoded = unicodedata.normalize('NFKD', text_encoded)

    return text_encoded

# Detect the source language for countries which have more official languages
TRANS_LANGUAGE_MAPPING = {
    # 'DE': lambda text: 'DE'
    "BE": get_detected_lang,
    "SE": get_detected_lang,
}
# import json
# import chardet
# import requests
# import transaction
# from requests.auth import HTTPDigestAuth


# For the following countries, the translation service uses
# different country code
ALTERNATE_COUNTRY_CODES = {
    "SI": "SL",
}


def get_mapped_language(country_code, text):
    detect_func = TRANS_LANGUAGE_MAPPING[country_code]
    detected_lang = detect_func(text)

    if not detected_lang:
        return country_code

    if detected_lang == "en":
        return country_code

    return detected_lang.upper()
