import logging
import os
from copy import deepcopy

import transaction
from Acquisition import aq_inner, aq_parent
from plone import api
from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.utils import iterSchemata
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Testing.ZopeTestCase import utils as zopeUtils
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from eea.climateadapt.browser.admin import force_unlock

from . import (
    retrieve_volto_html_translation,
)
from .constants import LANGUAGE_INDEPENDENT_FIELDS
# from .translate_obj import translate_obj

# steps => used to translate the entire website
# translate in one step (when object is published)
# translate async => manual action
# from .constants import contenttype_language_independent_fields

logger = logging.getLogger("eea.climateadapt")


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


cover_fixes = {"eea.climateadapt.cards_tile": fix_cards_tile}


def handle_cover_step_4(obj, trans_obj, language, reindex):
    try:
        data_tiles = obj.get_tiles()
        for data_tile in data_tiles:
            if data_tile["type"] == "eea.climateadapt.cards_tile":
                data_trans_tiles = obj.get_tiles()
                for data_trans_tile in data_trans_tiles:
                    fixer = cover_fixes.get(data_trans_tile["type"], None)
                    if fixer:
                        fixer(obj, trans_obj, data_tile,
                              data_trans_tile, language)

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

    return reindex


def sync_obj_layout(obj, trans_obj, reindex, async_request):
    force_unlock(obj)

    layout_en = obj.getLayout()
    default_view_en = obj.getDefaultPage()
    layout_default_view_en = None
    if default_view_en:
        try:
            trans_obj.setDefaultPage(default_view_en)
            reindex = True
        except Exception:
            logger.info("Can't set default page for: %s",
                        trans_obj.absolute_url())
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
    logger.info("Copy tiles from cover: %s", from_cover.absolute_url())
    logger.info("Copy tiles to cover: %s", to_cover.absolute_url())

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


def copy_tiles_to_translation(en_obj, trans_obj):
    tiles = [en_obj.get_tile(x) for x in en_obj.list_tiles()]
    trans_obj.cover_layout = en_obj.cover_layout
    copy_tiles(tiles, en_obj, trans_obj)


def create_translation_object(obj, language):
    """Create translation object for an obj"""
    tm = TranslationManager(obj)
    translations = tm.get_translations()

    if language in translations:
        logger.info("Skip creating translation. Already exists.")

        if obj.portal_type == "collective.cover.content":
            copy_tiles_to_translation(obj, translations[language])

        return

    check_full_path_exists(obj, language)
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

    if obj.portal_type == "collective.cover.content":
        copy_tiles_to_translation(obj, translated_object)

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


def is_volto_context(context):
    volto_contexts = ["/en/mission", "/en/observatory"]
    for value in volto_contexts:
        if value in context.absolute_url():
            return True
    return False


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


def execute_translate_async(en_obj, options, language, request_vars=None):
    """Executed via zc.async, triggers the call to eTranslation"""
    request_vars = request_vars or {}
    site_portal = portal.get()

    if not hasattr(site_portal, "REQUEST"):
        zopeUtils._Z2HOST = options["http_host"]
        en_obj = zopeUtils.makerequest(en_obj)
        server_url = site_portal.REQUEST.other["SERVER_URL"].replace(
            "http", "https")
        site_portal.REQUEST.other["SERVER_URL"] = server_url
        # context.REQUEST['PARENTS'] = [context]

        for k, v in request_vars.items():
            site_portal.REQUEST.set(k, v)

    # site_portal.REQUEST = en_obj.REQUEST

    create_translation_object(en_obj, language)

    http_host = options["http_host"]
    translations = TranslationManager(en_obj).get_translations()
    trans_obj = translations[language]
    trans_obj_url = trans_obj.absolute_url()
    trans_obj_path = "/cca" + trans_obj_url.split(http_host)[-1]
    options["trans_obj_path"] = trans_obj_path

    retrieve_volto_html_translation(
        options["http_host"],
        "en",
        options["html_content"].encode("utf-8"),
        options["trans_obj_path"],
        target_languages=language.upper(),
    )

    try:
        del site_portal.REQUEST
        del en_obj.REQUEST
    except AttributeError:
        pass
    logger.info("Async translate for object %s", options["obj_url"])
    return "Finished"

    # if options.get("is_volto", None) is not None:

    # NOTE: all the code below is for reference only. We only use the version above

    # if is_volto_context(context):
    #     logger.info("SKIP classic translation in volto context")
    #     return
    #
    # if not hasattr(context, "REQUEST"):
    #     zopeUtils._Z2HOST = options["http_host"]
    #     context = zopeUtils.makerequest(context)
    #     context.REQUEST.other["SERVER_URL"] = context.REQUEST.other[
    #         "SERVER_URL"
    #     ].replace("http", "https")
    #     # context.REQUEST['PARENTS'] = [context]
    #
    #     for k, v in request_vars.items():
    #         context.REQUEST.set(k, v)
    #
    # settings = {
    #     "language": language,
    #     "uid": options["uid"],
    # }
    #
    # trans_copy_field_data(context, settings, async_request=True)
    # site_portal = portal.get()
    # site_portal.REQUEST = context.REQUEST
    #
    # translate_obj(context, lang=language, one_step=True)
    # del site_portal.REQUEST
    #
    # logger.info("Async translate for object %s", options["obj_url"])
    #
    # return "Finished"


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
                or k in LANGUAGE_INDEPENDENT_FIELDS + ["cover_layout"]
                or k not in fielddata
            ):
                continue

            value = fielddata[k]
            if IRichText.providedBy(v):
                value = RichTextValue(value)
            setattr(trans_obj, k, value)

    if "cover_layout" in fielddata:
        coverdata = fielddata["cover_layout"]

        for tileid in coverdata.keys():
            full_tile_id = "plone.tiles.data.%s" % tileid

            # tile is missing in the translation, so we may copy it from the original
            tile = trans_obj.__annotations__.get(full_tile_id)
            if tile is None:
                tile = canonical.__annotations__.get(full_tile_id, None)
                if tile is None:
                    logger.warning(
                        "Tile is missing from both the original and the translation: %s / %s",
                        full_tile_id,
                        trans_obj.absolute_url(),
                    )
                    continue
                tile = deepcopy(tile)

            for fieldname, fieldvalue in coverdata[tileid].items():
                orig = tile[fieldname]
                if isinstance(orig, RichTextValue):
                    tile[fieldname] = RichTextValue(fieldvalue)
                else:
                    tile[fieldname] = fieldvalue
            trans_obj.__annotations__["plone.tiles.data.%s" % tileid] = tile

        trans_obj.__annotations__._p_changed = True
