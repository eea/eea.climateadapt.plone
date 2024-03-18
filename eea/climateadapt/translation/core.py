import json
import logging
import os

import transaction
from Acquisition import aq_inner, aq_parent
from plone import api
from plone.api import portal
from plone.app.multilingual.factory import DefaultTranslationFactory
from plone.app.multilingual.manager import TranslationManager
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Testing.ZopeTestCase import utils as zopeUtils
from zope.interface import alsoProvides

from eea.climateadapt.browser.admin import force_unlock

from . import (
    retrieve_volto_html_translation,
)
from .constants import contenttype_language_independent_fields
from .translate_obj import translate_obj
from .utils import get_object_fields_values

# steps => used to translate the entire website
# translate in one step (when object is published)
# translate async => manual action

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


def handle_cover_step_4(obj, trans_obj, language, reindex):
    try:
        data_tiles = obj.get_tiles()
        for data_tile in data_tiles:
            if data_tile["type"] == "eea.climateadapt.cards_tile":
                data_trans_tiles = obj.get_tiles()
                for data_trans_tile in data_trans_tiles:
                    if data_trans_tile["type"] == "eea.climateadapt.cards_tile":
                        tile = obj.get_tile(data_tile["id"])
                        try:
                            trans_tile = trans_obj.get_tile(data_trans_tile["id"])
                        except ValueError:
                            logger.info("Tile not found.")
                            trans_tile = None

                        if trans_tile is not None:
                            collection_obj = uuidToObject(tile.data["uuid"])
                            collection_trans_obj = get_translation_object(
                                collection_obj, language
                            )

                            dataManager = ITileDataManager(trans_tile)

                            temp = dataManager.get()
                            try:
                                temp["uuid"] = IUUID(collection_trans_obj)
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

    return reindex


def translation_step_4(site, request, async_request=False):
    # used for whole-site translation
    """Copy fields values from en to given language for language independent
        fields.
    TODO: this is used in a lot of places in code. It needs to be properly documented
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
            force_unlock(obj)

            layout_en = obj.getLayout()
            default_view_en = obj.getDefaultPage()
            layout_default_view_en = None
            if default_view_en:
                try:
                    trans_obj.setDefaultPage(default_view_en)
                    reindex = True
                except Exception:
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
                    trans_obj[default_view_en].setLayout(layout_default_view_en)
                except Exception:
                    logger.info("Can't set layout for: %s", trans_obj.absolute_url())
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
            except Exception:
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


def is_volto_context(context):
    volto_contexts = ["/en/mission", "/en/observatory"]
    for value in volto_contexts:
        if value in context.absolute_url():
            return True
    return False


def execute_translate_async(context, options, language, request_vars):
    """translate via zc.async"""
    if options.get("is_volto", None) is not None:
        retrieve_volto_html_translation(
            options["http_host"],
            "en",
            options["html_content"].encode("utf-8"),
            options["trans_obj_path"],
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
