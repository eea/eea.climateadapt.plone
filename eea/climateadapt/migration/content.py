import json
import logging

from collective.cover.interfaces import ICover
from collective.cover.tiles.embed import IEmbedTile
from collective.cover.tiles.richtext import IRichTextTile
from eea.climateadapt.migration.interfaces import IMigrateToVolto
from eea.climateadapt.tiles.cardslisting import ICardsTile
from eea.climateadapt.tiles.genericview import IGenericViewTile
from eea.climateadapt.tiles.richtext import IRichTextWithTitle
from eea.climateadapt.tiles.search_acecontent import (
    IFilterAceContentItemsTile, IRelevantAceContentItemsTile,
    ISearchAceContentTile)
from eea.climateadapt.tiles.shareinfo import IShareInfoTile
from eea.climateadapt.tiles.transregional_select import \
    ITransRegionalSelectTile
from plone.app.contenttypes.interfaces import IDocument, IFolder
from plone.tiles.interfaces import ITileDataManager
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer

from .fixes import fix_content
from .tiles import (cards_tile_to_block, embed_tile_to_block,
                    filter_acecontent_to_block, genericview_tile_to_block,
                    region_select_to_block, relevant_acecontent_to_block,
                    richtext_tile_to_blocks, search_acecontent_to_block,
                    share_info_tile_to_block)
from .utils import convert_to_blocks, make_uid

logger = logging.getLogger('MigrateContent')


tile_converters = {
    IRichTextTile: richtext_tile_to_blocks,
    IRichTextWithTitle: richtext_tile_to_blocks,
    ISearchAceContentTile: search_acecontent_to_block,
    IRelevantAceContentItemsTile: relevant_acecontent_to_block,
    IFilterAceContentItemsTile: filter_acecontent_to_block,
    IShareInfoTile: share_info_tile_to_block,
    ITransRegionalSelectTile: region_select_to_block,
    IEmbedTile: embed_tile_to_block,
    ICardsTile: cards_tile_to_block,
    IGenericViewTile: genericview_tile_to_block,
}


@adapter(ICover, Interface)
@implementer(IMigrateToVolto)
class MigrateCover(object):
    """ Migrate the tiles of a cover to volto blocks
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _blocklist_to_blocks(self, blockslist):
        blocks_layout = {"items": [b[0] for b in blockslist]}
        blocks_data = {}
        for b in blockslist:
            blocks_data[b[0]] = b[1]

        return blocks_data, blocks_layout

    def convert_tile_to_volto_blocklist(self, tileid):
        tile = self.context.get_tile(tileid)
        tile_dm = ITileDataManager(tile)
        schema = tile_dm.tileType.schema
        converter = tile_converters.get(schema, None)

        if not converter:
            logger.warning("You need to implement converter for block: %s", schema)
            return {"blocks": []}

        data = converter(tile_dm, self.context, self.request)
        if not data:
            logger.warning("Tile did not convert to blocks: %s", schema)
            return {"blocks": []}

        return data

    def make_column_block(self, row):
        attributes = {}
        col_mapping = {
            2: 'oneThird',
            3: 'oneThird',
            4: 'oneThird',
            6: 'halfWidth',
            8: 'twoThirds',
            9: 'twoThirds',
            10: 'twoThirds',
            12: 'full',
        }
        children = row['children']
        columns_storage = {
            "blocks": {},       # these are the columns
            "blocks_layout": {"items": []},
        }

        data = {
            "@type": "columnsBlock",
            "data": columns_storage,     # stores columns as "blocks"
            "gridSize": 12,
            "gridCols": [
                col_mapping[column['column-size']] for column in children
            ]}

        for column in children:
            uid = make_uid()

            blocks = {}
            blocks_layout = []

            for tile in column['children']:
                if tile.get('id', None) is None:
                    logger.warning("Implement row.")
                    continue
                    # TODO new row and columns case (recursive?)
                    # /cca/en/knowledge/tools/adaptation-support-tool/step-3-2/
                tile_data = self.convert_tile_to_volto_blocklist(tile['id'])
                blocklist = tile_data.pop('blocks', [])
                attributes.update(tile_data)
                tile_blocks, tile_blocks_layout = self._blocklist_to_blocks(
                    blocklist)
                blocks.update(tile_blocks)
                blocks_layout.extend(tile_blocks_layout['items'])

            columns_storage['blocks'][uid] = {
                "blocks": blocks,
                "blocks_layout": {"items": blocks_layout}
            }
            columns_storage['blocks_layout']['items'].append(uid)

        return [make_uid(), data]

    def __call__(self):
        # allow some blocks to set content metadata fields

        # todo: convert cover layout to columns block layout

        attributes = {}
        tiles = {}

        for tileid in self.context.list_tiles():
            data = self.convert_tile_to_volto_blocklist(tileid)
            tiles[tileid] = data
            # blocks.extend(data.pop('blocks', []))
            attributes.update(data)

        if len(tiles) == 1:
            blocks = []
            for data in tiles.values():
                blocks.extend(data.get('blocks', []))

            blocks_layout = {"items": [b[0] for b in blocks]}
            blocks_data = {}
            for b in blocks:
                blocks_data[b[0]] = b[1]

            self.context.blocks_layout = blocks_layout
            self.context.blocks = blocks_data
        else:
            cover_layout = json.loads(self.context.cover_layout)

            page_blocks = []

            for row in cover_layout:
                assert row['type'] == 'row'
                columns = row['children']
                if len(columns) > 1:
                    column = self.make_column_block(row)
                    page_blocks.append(column)
                else:
                    tiles = columns[0].get('children', None)
                    if tiles is None:
                        continue
                    for tile in tiles:
                        tileid = tile['id']
                        data = self.convert_tile_to_volto_blocklist(tileid)
                        tile_blocks = data.pop('blocks', [])
                        attributes.update(data)
                        page_blocks.extend(tile_blocks)

            blocks_layout = {"items": [b[0] for b in page_blocks]}
            blocks_data = {}
            for b in page_blocks:
                blocks_data[b[0]] = b[1]

            self.context.blocks_layout = blocks_layout
            self.context.blocks = blocks_data

        # TODO: ensure there's a page banner block (or title block)

        fix_content(self.context)

        # return json.dumps({"blocks": blocks, "attributes": attributes})


@adapter(IDocument, Interface)
@implementer(IMigrateToVolto)
class MigrateDocument(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context

        text = obj.text
        html = text.raw     # TODO: should we use .output ?
        blocks = convert_to_blocks(html)
        title_uid = make_uid()
        uids = [title_uid] + [b[0] for b in blocks]
        obj.blocks_layout = {"items": uids}
        _blocks = {}
        _blocks[title_uid] = {"@type": "title"}
        for (uid, block) in blocks:
            _blocks[uid] = block
        obj.blocks = _blocks
        obj._p_changed = True


@adapter(IFolder, Interface)
@implementer(IMigrateToVolto)
class MigrateFolder(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context
        default_page = obj.getProperty('default_page')
        if not default_page and "index_html" in obj.contentIds():
            default_page = 'index_html'

        if default_page:
            cover = obj.restrictedTraverse(default_page)
            unwrapped = cover.aq_inner.aq_self
            if not hasattr(unwrapped, 'blocks') or not unwrapped.blocks:
                migrate = getMultiAdapter(
                    (cover, self.request), IMigrateToVolto)
                migrate()

            self.context.blocks_layout = cover.blocks_layout
            self.context.blocks = cover.blocks
            self._p_changed = True
