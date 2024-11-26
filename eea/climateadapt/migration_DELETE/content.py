"""Plone Content Types content migrators"""

import json
import logging

# from collective.cover.interfaces import ICover
# from collective.cover.tiles.embed import IEmbedTile
# from collective.cover.tiles.richtext import IRichTextTile
from eea.climateadapt.translation.utils import translated_url
from plone.app.contenttypes.interfaces import (
    IDocument,
    IEvent,
    IFolder,
    INewsItem,
    ILink,
)
from plone.dexterity.interfaces import IDexterityContent
# from plone.tiles.interfaces import ITileDataManager
from zope.component import adapter, queryMultiAdapter
from zope.interface import Interface, implementer

from eea.climateadapt.browser.tilehelpers import ICarousel
from eea.climateadapt.migration.interfaces import IMigrateToVolto
from eea.climateadapt.tiles.ast import (
    IASTHeaderTile,
    IASTNavigationTile,
    IUrbanASTNavigationTile,
)
from eea.climateadapt.tiles.cardslisting import ICardsTile
from eea.climateadapt.tiles.country_select import ICountrySelectTile
from eea.climateadapt.tiles.formtile import IFormTile
from eea.climateadapt.tiles.genericview import IGenericViewTile
from eea.climateadapt.tiles.richtext import IRichTextWithTitle
from eea.climateadapt.tiles.search_acecontent import (
    IFilterAceContentItemsTile,
    IRelevantAceContentItemsTile,
    ISearchAceContentTile,
)
from eea.climateadapt.tiles.section_nav import ISectionNavTile
from eea.climateadapt.tiles.shareinfo import IShareInfoTile
from eea.climateadapt.tiles.transregional_select import ITransRegionalSelectTile

from .blocks import (
    make_folder_listing_block,
    make_narrow_layout_block,
    make_summary_block,
    make_title_block,
)
from .config import COL_MAPPING, IGNORED_CONTENT_TYPES, IGNORED_PATHS, LANGUAGES
from .fixes import fix_content, fix_folder, fix_layout_size
from .tiles import (
    cards_tile_to_block,
    embed_tile_to_block,
    filter_acecontent_to_block,
    genericview_tile_to_block,
    region_select_to_block,
    relevant_acecontent_to_block,
    richtext_tile_to_blocks,
    search_acecontent_to_block,
    share_info_tile_to_block,
)
from .utils import convert_to_blocks, get_country_alpha2, make_uid, path

logger = logging.getLogger("ContentMigrate")
logger.setLevel(logging.INFO)


def nop_tile(tile_dm, obj, request):
    return {"blocks": []}


def country_select_tile(data, obj, request):
    flag_uid = make_uid()
    iso = get_country_alpha2(obj.Title())
    group_blocks = {}
    group_blocks[flag_uid] = {
        "@type": "countryFlag",
        "country_name": iso,
        "show_dropdown": True,
        "show_flag": True,
        "show_name": True,
    }
    group_blocks_layout = {"items": [flag_uid]}
    block = {
        "@type": "group",
        "as": "div",
        "data": {
            "blocks": group_blocks,
            "blocks_layout": group_blocks_layout,
        },
        "styles": {
            "size": "container_width",
            "style_name": "content-box-primary",
            "useAsPageHeader": True,
        },
    }
    return {"blocks": [[make_uid(), block]]}


tile_converters = {
    # IRichTextTile: richtext_tile_to_blocks,
    IRichTextWithTitle: richtext_tile_to_blocks,
    ISearchAceContentTile: search_acecontent_to_block,
    IRelevantAceContentItemsTile: relevant_acecontent_to_block,
    IFilterAceContentItemsTile: filter_acecontent_to_block,
    IShareInfoTile: share_info_tile_to_block,
    ITransRegionalSelectTile: region_select_to_block,
    # IEmbedTile: embed_tile_to_block,
    ICardsTile: cards_tile_to_block,
    IGenericViewTile: genericview_tile_to_block,
    # used in country profile page, no migration for now
    ICountrySelectTile: country_select_tile,
    # eea.climateadapt.browser.tilehelpers.ICarousel
    #
    #
    ISectionNavTile: nop_tile,  # use context navigation
    IASTNavigationTile: nop_tile,  # use context navigation
    IASTHeaderTile: nop_tile,  # use EEA DS banner subtitle
    IUrbanASTNavigationTile: nop_tile,  # use context navigation
    IFormTile: nop_tile,  # no migration
    ICarousel: nop_tile,  # no migration
}


# @adapter(ICover, Interface)
# @implementer(IMigrateToVolto)
# class MigrateCover(object):
#     """Migrate the tiles of a cover to volto blocks"""

#     def __init__(self, context, request):
#         self.context = context
#         self.request = request

#     def _blocklist_to_blocks(self, blockslist):
#         blocks_layout = {"items": [b[0] for b in blockslist]}
#         blocks_data = {}
#         for b in blockslist:
#             blocks_data[b[0]] = b[1]

#         return blocks_data, blocks_layout

#     def convert_tile_to_volto_blocklist(self, tileid):
#         tile = self.context.get_tile(tileid)
#         tile_dm = ITileDataManager(tile)
#         schema = tile_dm.tileType.schema
#         converter = tile_converters.get(schema, None)

#         if not converter:
#             logger.warning("You need to implement converter for block: %s", schema)
#             return {"blocks": []}

#         data = converter(tile_dm, self.context, self.request)
#         if not data:
#             logger.warning("Tile did not convert to blocks: %s", schema)
#             return {"blocks": []}

#         return data

#     def make_column_block(self, row):
#         attributes = {}
#         children = row["children"]
#         columns_storage = {
#             "blocks": {},  # these are the columns
#             "blocks_layout": {"items": []},
#         }

#         data = {
#             "@type": "columnsBlock",
#             "data": columns_storage,  # stores columns as "blocks"
#             "gridSize": 12,
#             "gridCols": [COL_MAPPING[column["column-size"]] for column in children],
#         }

#         for column in children:
#             uid = make_uid()

#             blocks = {}
#             blocks_layout = []

#             for tile in column["children"]:
#                 if tile.get("type") == "row":
#                     # some of the columns haven't been filled
#                     if not tile.get("children"):
#                         continue

#                     # this type of content is a nasty inherited since the migration of
#                     # content from Liferea, due to the lack of nested columns in
#                     # collective.cover
#                     # So we convert this row to a separate columns block
#                     (block_id, blockdata) = self.make_column_block(tile)
#                     blocks[block_id] = blockdata
#                     blocks_layout.append(block_id)
#                     continue

#                 if tile.get("id", None) is None:
#                     logger.warning("Implement row.")
#                     continue
#                     # TODO new row and columns case (recursive?)
#                     # /cca/en/knowledge/tools/adaptation-support-tool/step-3-2/
#                 tile_data = self.convert_tile_to_volto_blocklist(tile["id"])
#                 blocklist = tile_data.pop("blocks", [])
#                 attributes.update(tile_data)
#                 tile_blocks, tile_blocks_layout = self._blocklist_to_blocks(blocklist)
#                 blocks.update(tile_blocks)
#                 blocks_layout.extend(tile_blocks_layout["items"])

#             columns_storage["blocks"][uid] = {
#                 "blocks": blocks,
#                 "blocks_layout": {"items": blocks_layout},
#             }
#             columns_storage["blocks_layout"]["items"].append(uid)

#         return [make_uid(), data]

#     def __call__(self):
#         # allow some blocks to set content metadata fields
#         # todo: convert cover layout to columns block layout

#         attributes = {}
#         tiles = {}

#         for tileid in self.context.list_tiles():
#             data = self.convert_tile_to_volto_blocklist(tileid)
#             tiles[tileid] = data
#             # blocks.extend(data.pop('blocks', []))
#             attributes.update(data)

#         if len(tiles) == 1:
#             blocks = []
#             for data in list(tiles.values()):
#                 blocks.extend(data.get("blocks", []))

#             title_uid, titleblock = make_title_block()
#             blocks_layout = {"items": [title_uid] + [b[0] for b in blocks]}
#             blocks_data = {}
#             blocks_data[title_uid] = titleblock

#             for uid, block in blocks:
#                 blocks_data[uid] = block

#             self.context.blocks_layout = blocks_layout
#             self.context.blocks = blocks_data
#         else:
#             cover_layout = []

#             if self.context.cover_layout:
#                 cover_layout = json.loads(self.context.cover_layout)
#             else:
#                 logger.warning("No cover layout at %s", self.context.absolute_url())

#             page_blocks = []

#             for row in cover_layout:
#                 assert row["type"] == "row"
#                 columns = row["children"]
#                 if len(columns) > 1:
#                     column = self.make_column_block(row)
#                     page_blocks.append(column)
#                 else:
#                     tiles = columns[0].get("children", None)
#                     if tiles is None:
#                         continue
#                     for tile in tiles:
#                         tileid = tile["id"]
#                         data = self.convert_tile_to_volto_blocklist(tileid)
#                         tile_blocks = []
#                         if "blocks" in data:
#                             tile_blocks = data.pop("blocks")
#                         attributes.update(data)
#                         page_blocks.extend(tile_blocks)

#             titleuid, titleblock = make_title_block()
#             blocks_layout = {"items": [titleuid] + [b[0] for b in page_blocks]}
#             blocks_data = {}
#             blocks_data[titleuid] = titleblock

#             for uid, block in page_blocks:
#                 blocks_data[uid] = block

#             self.context.blocks_layout = blocks_layout
#             self.context.blocks = blocks_data

#         # TODO: ensure there's a page banner block (or title block)

#         fix_content(self.context)
#         self.context.reindexObject()


@adapter(IDocument, Interface)
@implementer(IMigrateToVolto)
class MigrateDocument(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context

        text = obj.text
        title_uid = make_uid()

        if not text:
            obj.blocks = {}
            obj.blocks[title_uid] = {"@type": "title", "hideContentType": True}
            obj.blocks_layout = {"items": [title_uid]}
            obj._p_changed = True

            return

        html = text.raw  # TODO: should we use .output ?
        try:
            blocks = convert_to_blocks(html)
        except ValueError:
            logger.error("Error in blocks converter: %s", path(obj))
            blocks = []

        uids = [title_uid] + [b[0] for b in blocks]
        obj.blocks_layout = {"items": uids}
        _blocks = {}
        _blocks[title_uid] = {"@type": "title", "hideContentType": True}
        for uid, block in blocks:
            _blocks[uid] = block
        obj.blocks = _blocks
        obj._p_changed = True
        fix_content(self.context)
        fix_layout_size(obj)

        obj.reindexObject()


def is_ignored_path(path):
    for lang in LANGUAGES:
        for test_path in IGNORED_PATHS:
            test_path = test_path.replace("{lang}", lang)
            if path.startswith(test_path) or path.startswith("cca/" + test_path):
                return True


def migrate_content_to_volto(obj, request):
    if obj.portal_type in IGNORED_CONTENT_TYPES:
        return

    url = obj.absolute_url(relative=True)

    if is_ignored_path(url):
        return

    if not IDexterityContent.providedBy(obj):
        logger.debug("Ignoring %s, not a dexterity content", url)
        return

    # from plone.api.content import get_state
    # try:
    #     state = get_state(obj)
    # except Exception:
    #     logger.warn("Unable to get review state for %s", url)
    # else:
    #     if state in ['private', 'archived']:
    #         logger.debug("Skip migrating %s as it's private/archived", url)
    #         return

    logger.info("Migrating %s" % url)

    migrate = queryMultiAdapter((obj, request), IMigrateToVolto)
    if migrate is None:
        logger.warning("No migrator for %s", url)
        return

    try:
        migrate()
    except Exception:
        logger.exception("Error in migrating %s" % url)

    obj.reindexObject()


@adapter(IFolder, Interface)
@implementer(IMigrateToVolto)
class MigrateFolder(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context
        # request = self.request
        default_page = obj.getProperty("default_page")
        if not default_page and "index_html" in obj.contentIds():
            default_page = "index_html"

        if default_page:
            cover = obj.restrictedTraverse(default_page)

            # always forcing migration of blocks for the default page
            migrate_content_to_volto(cover, self.request)

            # unwrapped = cover.aq_inner.aq_self
            # if not hasattr(unwrapped, "blocks") or not unwrapped.blocks:
            #     migrate_content_to_volto(cover, self.request)

            self.context.blocks_layout = cover.blocks_layout
            self.context.blocks = cover.blocks

            obj.title = cover.title
            obj.description = cover.description
            self._p_changed = True

            fix_content(obj)
        else:
            listuid, listblock = make_folder_listing_block()
            blocks = {}
            blocks[listuid] = listblock
            titleuid, titleblock = make_title_block()
            blocks[titleuid] = titleblock
            self.context.blocks_layout = {"items": [titleuid, listuid]}
            self.context.blocks = blocks

        fix_folder(obj)

        obj.reindexObject()


def migrate_simplecontent_to_volto(obj, make_metadata_blocks):
    blocks = {}
    items = []

    titleuid, titleblock = make_title_block()
    titleblock["hideContentType"] = False
    blocks[titleuid] = titleblock
    items.append(titleuid)

    metadatablocks = make_metadata_blocks()

    voltoblocks = []

    if obj.text:
        if isinstance(obj.text, str):
            text = obj.text
        else:
            text = obj.text.raw
        voltoblocks = convert_to_blocks(text)

    for buid, block in metadatablocks + voltoblocks:
        blocks[buid] = block
        items.append(buid)

    obj.blocks = blocks
    obj.blocks_layout = {"items": items}

    obj._p_changed = True


@adapter(INewsItem, Interface)
@implementer(IMigrateToVolto)
class MigrateNewsItem(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        def make_metadata_blocks():
            sumuid, sumblock = make_summary_block()
            layoutuid, layout = make_narrow_layout_block()
            return [[sumuid, sumblock], [layoutuid, layout]]

        migrate_simplecontent_to_volto(self.context, make_metadata_blocks)
        self.context.reindexObject()


@adapter(IEvent, Interface)
@implementer(IMigrateToVolto)
class MigrateEvent(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        def make_metadata_blocks():
            sumuid, sumblock = make_summary_block()
            return [[sumuid, sumblock]]

        migrate_simplecontent_to_volto(self.context, make_metadata_blocks)
        self.context.reindexObject()


@adapter(ILink, Interface)
@implementer(IMigrateToVolto)
class MigrateLink(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if self.context.remoteUrl:
            url = self.context.remoteUrl
            url = translated_url(self.context, url, self.context.language)
            if url != self.context.remoteUrl:
                logger.info(
                    "Fix link %s => %s (%s)",
                    self.context.remoteUrl,
                    url,
                    self.context.absolute_url(),
                )
                self.context.remoteUrl = url
                self.context.reindexObject()


@adapter(Interface, Interface)
@implementer(IMigrateToVolto)
class MigrateFallback(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        logger.info(
            "Fallback migrator for (%s) %s",
            self.context.portal_type,
            self.context.absolute_url(),
        )
