# import json

from collective.cover.interfaces import ICover
from collective.cover.tiles.richtext import IRichTextTile
from eea.climateadapt.migration.interfaces import IMigrateToVolto
from eea.climateadapt.tiles.richtext import IRichTextWithTitle
from plone.tiles.interfaces import ITileDataManager
from zope.component import adapter
from zope.interface import Interface, implementer

from .utils import convert_to_blocks


def richtext_tile_to_blocks(tile_dm, obj, request):
    attributes = {}
    data = tile_dm.get()
    title_level = data.get('title_level')
    title = data.get('title')

    if title_level == 'h1' and title:
        attributes['title'] = title

    blocks = []
    text = data.get('text')
    if text:
        html = text.raw     # TODO: should we use .output ?
        print("Converting--")
        print(html)
        print("--/Converting")
        blocks = convert_to_blocks(html)

    return {
        "blocks": blocks,
    }


tile_converters = {
    IRichTextTile: richtext_tile_to_blocks,
    IRichTextWithTitle: richtext_tile_to_blocks
}


@adapter(ICover, Interface)
@implementer(IMigrateToVolto)
class MigrateCover(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # allow some blocks to set content metadata fields
        attributes = {}
        blocks = []

        for tileid in self.context.list_tiles():
            tile = self.context.get_tile(tileid)
            tile_dm = ITileDataManager(tile)
            schema = tile_dm.tileType.schema
            converter = tile_converters[schema]
            data = converter(tile_dm, self.context, self.request)
            blocks.extend(data.pop('blocks', []))
            attributes.update(data)

        blocks_layout = {"items": [b[0] for b in blocks]}
        blocks_data = {}
        for b in blocks:
            blocks_data[b[0]] = b[1]

        self.context.blocks_layout = blocks_layout
        self.context.blocks = blocks_data
        return "ok"
        # print(blocks)
        # return json.dumps({"blocks": blocks, "attributes": attributes})
