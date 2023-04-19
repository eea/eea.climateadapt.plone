import json
from uuid import uuid4

from collective.cover.interfaces import ICover
from collective.cover.tiles.richtext import IRichTextTile
from eea.climateadapt.migration.interfaces import IMigrateToVolto
from eea.climateadapt.tiles.richtext import IRichTextWithTitle
from eea.climateadapt.tiles.search_acecontent import ISearchAceContentTile
from eea.climateadapt.tiles.shareinfo import IShareInfoTile
from eea.climateadapt.config import DEFAULT_LOCATIONS
from eea.climateadapt.translation.utils import (get_current_language)
from plone.app.contenttypes.interfaces import IFolder
from plone.tiles.interfaces import ITileDataManager
from zope.component import adapter
from zope.interface import Interface, implementer
from zope.component.hooks import getSite

from .fixes import fix_content
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


def search_acecontent_to_block(tile_dm, obj, request):
    data = tile_dm.get()

    blocks = [[make_uid(), {
        "@type": "searchAceContent",
        "title": data.get('title'),
        "search_text": data.get('search_text'),
        "origin_website": data.get('origin_website'),
        "search_type": data.get('search_type'),
        "element_type": data.get('element_type'),
        "sector": data.get('sector'),
        "special_tags": data.get('special_tags'),
        'countries': data.get('countries'),
        "macro_regions": data.get('macro_regions'),
        "bio_regions": data.get('bio_regions'),
        "funding_programme": data.get('funding_programme'),
        "nr_items": data.get('nr_items'),
    }]]

    return {
        "blocks": blocks,
    }

def share_info_tile_to_block(tile_dm, obj, request):
    data = tile_dm.get()

    def link_url(obj):
        site = getSite()
        current_lang = get_current_language(obj, request)
        type_ = data.get('shareinfo_type')
        location, _t, factory = DEFAULT_LOCATIONS[type_]
        location = current_lang + '/' + location
        location = site.restrictedTraverse(location)
        url = location.absolute_url().replace("/" + current_lang + "/", "/en/")
        return "{0}/++add++{1}".format(url, factory)


    blocks = [[make_uid(), {
        "@type": "callToActionBlock",
        "href": link_url(obj),
        "styles": {
            "icon": "ri-share-line",
            "theme": "primary"
        },
        "text": "Share your information", # TODO: translation
        "target": "_self",
    }]]

    return {
        "blocks": blocks,
    }


tile_converters = {
    IRichTextTile: richtext_tile_to_blocks,
    IRichTextWithTitle: richtext_tile_to_blocks,
    ISearchAceContentTile: search_acecontent_to_block,
    IShareInfoTile: share_info_tile_to_block,
}


def make_uid():
    return str(uuid4())


@adapter(ICover, Interface)
@implementer(IMigrateToVolto)
class MigrateCover(object):
    """
[{u'children': [{u'children': [{u'id': u'1ab374eb8fb84e7ca45d45c6ed478889',
                                u'tile-type': u'eea.climateadapt.richtext_with_title',
                                u'type': u'tile'}],
                 u'column-size': 9,
                 u'css-class': u'content-column',
                 u'roles': [u'Manager'],
                 u'type': u'group'},
                {u'children': [{u'id': u'8df509b8122b48eaac79b3f2a4cfba83',
                                u'tile-type': u'eea.climateadapt.transregionselect',
                                u'type': u'tile'},
                               {u'id': u'f9c70eef-6442-4f00-b680-6012397531b0',
                                u'tile-type': u'eea.climateadapt.search_acecontent',
                                u'type': u'tile'}],
                 u'column-size': 3,
                 u'css-class': u'content-sidebar',
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'}]

[{u'children': [{u'children': [{u'id': u'd2ff69d4-9a08-489a-9f10-a5e2340beb68',
                                u'tile-type': u'eea.climateadapt.richtext_with_title',
                                u'type': u'tile'}],
                 u'column-size': 8,
                 u'id': u'group1',
                 u'roles': [u'Manager'],
                 u'type': u'group'},
                {u'children': [{u'id': u'fb3101ae-c16f-4ee6-8e43-b5c6d81b7a4a',
                                u'tile-type': u'eea.climateadapt.search_acecontent',
                                u'type': u'tile'},
                               {u'id': u'd43dcc10-4529-4ed4-afd6-1888a241671a',
                                u'tile-type': u'collective.cover.richtext',
                                u'type': u'tile'}],
                 u'column-size': 4,
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'},
 {u'children': [{u'children': [{u'id': u'df0fcc4c-94a3-4b90-88c7-821158e2ac9c',
                                u'tile-type': u'collective.cover.richtext',
                                u'type': u'tile'}],
                 u'column-size': 12,
                 u'roles': [u'Manager'],
                 u'type': u'group'}],
  u'type': u'row'}]

{
  full: {
    mobile: 12,
    tablet: 12,
    computer: 12,
  },
  halfWidth: {
    mobile: 12,
    tablet: 6,
    computer: 6,
  },
  twoThirds: {
    mobile: 12,
    tablet: 8,
    computer: 8,
  },
  oneThird: {
    mobile: 12,
    tablet: 4,
    computer: 4,
  },
  halfWidthBig: {
    mobile: 12,
    tablet: 8,
    computer: 6,
  },
  oneThirdSmall: {
    mobile: 12,
    tablet: 2,
    computer: 3,
  },
  oneQuarter: {
    mobile: 12,
    tablet: 6,
    computer: 3,
  },
  oneFifth: {
    mobile: 12,
    tablet: 2,
    computer: 3,
  },
  fourFifths: {
    mobile: 12,
    tablet: 10,
    computer: 9,
  },
  twoFifths: {
    mobile: 12,
    tablet: 10,
    computer: 5,
  },
  threeFifths: {
    mobile: 12,
    tablet: 10,
    computer: 7,
  },
};

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
            print("You need to implement converter for block: ", schema)
            data = []
            return {"blocks": []}

        data = converter(tile_dm, self.context, self.request)

        return data

    def make_column_block(self, row):
        attributes = {}
        col_mapping = {
            9: 'twoThirds',
            3: 'oneThird',
            4: 'oneThird',
            8: 'twoThirds',
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
                    tiles = columns[0]['children']
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
        return "ok"

        # print(blocks)
        # return json.dumps({"blocks": blocks, "attributes": attributes})


@adapter(IFolder, Interface)
@implementer(IMigrateToVolto)
class MigrateFolder(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = self.context
        if "index_html" in obj.contentIds():
            cover = obj["index_html"]
            MigrateCover(cover, self.request).__call__()

        # if there's a cover with id index_html, use that as content
        pass
