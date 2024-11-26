import logging
from copy import deepcopy

from Acquisition import aq_inner, aq_parent
from eea.climateadapt.browser.admin import force_unlock
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
from zope.component.hooks import setSite
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from . import retrieve_volto_html_translation
from .constants import LANGUAGE_INDEPENDENT_FIELDS

logger = logging.getLogger("eea.climateadapt")


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
    """Used by save_html_volto. Adapts the cover data from one cover to another"""

    data_tiles = obj.get_tiles()

    for data_tile in data_tiles:
        if data_tile["type"] == "eea.climateadapt.cards_tile":
            data_trans_tiles = obj.get_tiles()
            for data_trans_tile in data_trans_tiles:
                fixer = cover_fixes.get(data_trans_tile["type"], None)
                if fixer:
                    fixer(obj, trans_obj, data_tile, data_trans_tile, language)

        if data_tile["type"] == "eea.climateadapt.relevant_acecontent":
            tile_id = data_tile["id"]
            plone_tile_id = "plone.tiles.data" + tile_id
            trans_tile = trans_obj.__annotations__.get(plone_tile_id) or {}
            saved_title = trans_tile.get("title")

            from_data = obj.__annotations__.get(plone_tile_id, None)
            if from_data:
                data = deepcopy(from_data)
                if saved_title:
                    data["title"] = saved_title

                trans_obj.__annotations__[plone_tile_id] = data

    force_unlock(obj)
    layout_en = obj.getLayout()
    if layout_en:
        reindex = True
        trans_obj.setLayout(layout_en)

    return reindex


def sync_obj_layout(obj, trans_obj, reindex, async_request):
    """Used by save_html_volto"""
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
    for a_type in list(tiles_types.keys()):
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
            # import pdb
            #
            # pdb.set_trace()


def check_full_path_exists(obj, language, site_portal):
    """Create full path for a object"""

    parent = aq_parent(aq_inner(obj))
    path = parent.getPhysicalPath()

    if len(path) <= 2:  # aborting, we've reached bottom
        return True

    translations = TranslationManager(parent).get_translations()
    if language not in translations:
        # TODO, what if the parent path already exist in language
        # but is not linked in translation manager
        create_translation_object(parent, language, site_portal)


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


def copy_tiles_to_translation(en_obj, trans_obj, site_portal):
    trans_obj_path = "/".join(trans_obj.getPhysicalPath())
    trans_obj = wrap_in_aquisition(trans_obj_path, site_portal)
    tiles = [en_obj.get_tile(x) for x in en_obj.list_tiles()]
    trans_obj.cover_layout = en_obj.cover_layout
    copy_tiles(tiles, en_obj, trans_obj)


def create_translation_object(obj, language, site_portal):
    """Create translation object for an obj"""
    # rc = RequestContainer(REQUEST=obj.REQUEST)
    tm = TranslationManager(obj)
    translations = tm.get_translations()

    if language in translations:
        logger.info("Skip creating translation. Already exists.")
        trans_obj = translations[language]

        if obj.portal_type == "collective.cover.content":
            copy_tiles_to_translation(obj, trans_obj, site_portal)

        sync_translation_state(trans_obj, obj)
        trans_obj.reindexObject()

        return translations[language]

    check_full_path_exists(obj, language, site_portal)
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
        copy_tiles_to_translation(obj, translated_object, site_portal)

    copy_missing_interfaces(obj, translated_object)
    sync_translation_state(translated_object, obj)

    translated_object.reindexObject()

    return translated_object


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


def sync_translation_state(trans_obj, en_obj):
    state = None

    try:
        state = api.content.get_state(en_obj)
    except WorkflowException:
        logger.error("Can't get state for original object: %s", en_obj)
        pass

    if state in ["published", "archived"]:
        if api.content.get_state(trans_obj) != state:
            wftool = getToolByName(trans_obj, "portal_workflow")
            logger.info("%s %s", state, trans_obj.absolute_url())
            if state == "published":
                wftool.doActionFor(trans_obj, "publish")
            elif state == "archived":
                wftool.doActionFor(trans_obj, "archive")

    if en_obj.EffectiveDate() != trans_obj.EffectiveDate():
        trans_obj.setEffectiveDate(en_obj.effective_date)
        trans_obj._p_changed = True
        # trans_obj.reindexObject()


def wrap_in_aquisition(obj_path, portal_obj):
    portal_path = portal_obj.getPhysicalPath()
    bits = obj_path.split("/")[len(portal_path):]

    base = portal_obj
    obj = base

    for bit in bits:
        obj = base.restrictedTraverse(bit).__of__(base)
        base = obj

    return obj


def execute_translate_async(en_obj, options, language):
    """Executed via zc.async, triggers the call to eTranslation"""

    en_obj_path = "/".join(en_obj.getPhysicalPath())

    environ = {
        "SERVER_NAME": options["http_host"],
        "SERVER_PORT": 443,
        "REQUEST_METHOD": "POST",
    }
    site_portal = portal.get()

    if not hasattr(site_portal, "REQUEST"):
        zopeUtils._Z2HOST = options["http_host"]
        site_portal = zopeUtils.makerequest(site_portal, environ)
        server_url = site_portal.REQUEST.other["SERVER_URL"].replace(
            "http", "https")
        site_portal.REQUEST.other["SERVER_URL"] = server_url
        setSite(site_portal)
        # context.REQUEST['PARENTS'] = [context]

        # for k, v in request_vars.items():
        #     site_portal.REQUEST.set(k, v)

    # this causes the modified event in plone.app.multilingual to skip some processing which otherwise crashes
    site_portal.REQUEST.translation_info = {"tg": True}

    en_obj = site_portal.restrictedTraverse(en_obj_path)
    en_obj = wrap_in_aquisition(en_obj_path, site_portal)

    # trans_obj = site_portal.restrictedTraverse(trans_obj_path)
    trans_obj = create_translation_object(en_obj, language, site_portal)
    trans_obj_path = "/".join(trans_obj.getPhysicalPath())

    retrieve_volto_html_translation(
        options["http_host"],
        "en",
        options["html_content"].encode("utf-8"),
        trans_obj_path,
        target_languages=language.upper(),
    )

    try:
        del site_portal.REQUEST
        del en_obj.REQUEST
        del trans_obj.REQUEST
    except AttributeError:
        pass

    logger.info("Async translate for object %s", options["obj_url"])
    return "Finished"


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

        for tileid in list(coverdata.keys()):
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

            for fieldname, fieldvalue in list(coverdata[tileid].items()):
                orig = tile[fieldname]
                if isinstance(orig, RichTextValue):
                    tile[fieldname] = RichTextValue(fieldvalue)
                else:
                    tile[fieldname] = fieldvalue
            trans_obj.__annotations__["plone.tiles.data.%s" % tileid] = tile

        trans_obj.__annotations__._p_changed = True
