""" Post-migration "fixers", which are executed after an object has been migrated
"""


import logging

from plone.app.multilingual.api import get_translation_manager
from plone.tiles.interfaces import ITileDataManager

from .blocks import (
    make_events_archive_block,
    make_obs_countries_header,
    make_vibriomap_block,
    simple_slate_to_volto_blocks,
)
from .config import (
    AST_PATHS,
    FULL_PAGE_PATHS,
    LANGUAGES,
    SECTOR_POLICY_PATHS,
    TOP_LEVEL,
)
from .utils import get_country_alpha2, make_uid

logger = logging.getLogger()


languages = [lang for lang in LANGUAGES if lang != "en"]


def onpath(path):
    def decorator_factory(func):
        def decorator(context):
            url = context.absolute_url(relative=True)
            # print("test onpath", url)
            if not url.endswith(path):
                return
            return func(context)

        return decorator

    return decorator_factory


def inpath(path):
    def decorator_factory(func):
        def decorator(context):
            url = context.absolute_url(relative=True)
            # print("test inpath", url)
            if path not in url:
                return
            return func(context)

        return decorator

    return decorator_factory


def are_on_path(url, paths):
    for path in paths:
        if url.endswith(path):
            return True


def are_in_path(url, paths):
    for path in paths:
        if path in url:
            return True


def get_block_id(blocks, type):
    block = {k for k, v in blocks.items() if v["@type"] == type}
    if block:
        return list(block)[0]
    else:
        return None


@onpath("/knowledge/adaptation-information/climate-services/climate-services")
def fix_climate_services_toc(context):
    # in first column block, replace the first paragraph with a horizontal navigation table of contents

    col_block_id = context.blocks_layout["items"][1]  # [0] is title block
    col = context.blocks[col_block_id]
    column_ids = col["data"]["blocks_layout"]["items"]
    first_col_id = column_ids[0]
    first_col = col["data"]["blocks"][first_col_id]

    first_block_id = first_col["blocks_layout"]["items"][0]
    new_data = {"@type": "toc", "variation": "horizontalMenu"}
    first_col["blocks"][first_block_id] = new_data


@inpath("/observatory/evidence/projections-and-tools/ecdc-vibrio-map-viewer")
def fix_vibiomapviewer(context):
    # in first column block, replace the first paragraph with a horizontal navigation table of contents
    uid, block = make_vibriomap_block()
    context.blocks[uid] = block
    context.blocks_layout["items"].append(uid)


@onpath("/help/Webinars")
def fix_webinars(context):
    blocks = context.blocks
    layout = context.blocks_layout

    videos = {
        1: {
            "text": {"id": layout["items"][-1], "block": blocks[layout["items"][-1]]},
            "video": {"id": layout["items"][-2], "block": blocks[layout["items"][-2]]},
        },
        2: {
            "text": {"id": layout["items"][-3], "block": blocks[layout["items"][-3]]},
            "video": {"id": layout["items"][-4], "block": blocks[layout["items"][-4]]},
        },
        3: {
            "text": {"id": layout["items"][-5], "block": blocks[layout["items"][-5]]},
            "video": {"id": layout["items"][-6], "block": blocks[layout["items"][-6]]},
        },
        4: {
            "text": {"id": layout["items"][-7], "block": blocks[layout["items"][-7]]},
            "video": {"id": layout["items"][-8], "block": blocks[layout["items"][-8]]},
        },
        5: {
            "text": {"id": layout["items"][-9], "block": blocks[layout["items"][-9]]},
            "video": {
                "id": layout["items"][-10],
                "block": blocks[layout["items"][-10]],
            },
        },
    }

    col_1_id = make_uid()
    col_1_item_1_id = make_uid()

    col_2_id = make_uid()
    col_2_item_1_id = make_uid()
    col_2_item_2_id = make_uid()

    col_3_id = make_uid()
    col_3_item_1_id = make_uid()
    col_3_item_2_id = make_uid()

    blocks[col_1_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_1_item_1_id: {
                    "blocks": {
                        videos[1]["video"]["id"]: videos[1]["video"]["block"],
                        videos[1]["text"]["id"]: videos[1]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[1]["video"]["id"],
                            videos[1]["text"]["id"],
                        ]
                    },
                },
            },
            "blocks_layout": {
                "items": [
                    col_1_item_1_id,
                ]
            },
        },
        "gridCols": ["halfWidth", "halfWidth"],
        "gridSize": 12,
        "styles": {},
    }

    blocks[col_2_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_2_item_1_id: {
                    "blocks": {
                        videos[2]["video"]["id"]: videos[2]["video"]["block"],
                        videos[2]["text"]["id"]: videos[2]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[2]["video"]["id"],
                            videos[2]["text"]["id"],
                        ]
                    },
                },
                col_2_item_2_id: {
                    "blocks": {
                        videos[3]["video"]["id"]: videos[3]["video"]["block"],
                        videos[3]["text"]["id"]: videos[3]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[3]["video"]["id"],
                            videos[3]["text"]["id"],
                        ]
                    },
                },
            },
            "blocks_layout": {
                "items": [
                    col_2_item_2_id,
                    col_2_item_1_id,
                ]
            },
        },
        "gridCols": ["halfWidth", "halfWidth"],
        "gridSize": 12,
        "styles": {},
    }

    blocks[col_3_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_3_item_1_id: {
                    "blocks": {
                        videos[4]["video"]["id"]: videos[4]["video"]["block"],
                        videos[4]["text"]["id"]: videos[4]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[4]["video"]["id"],
                            videos[4]["text"]["id"],
                        ]
                    },
                },
                col_3_item_2_id: {
                    "blocks": {
                        videos[5]["video"]["id"]: videos[5]["video"]["block"],
                        videos[5]["text"]["id"]: videos[5]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[5]["video"]["id"],
                            videos[5]["text"]["id"],
                        ]
                    },
                },
            },
            "blocks_layout": {
                "items": [
                    col_3_item_2_id,
                    col_3_item_1_id,
                ]
            },
        },
        "gridCols": ["halfWidth", "halfWidth"],
        "gridSize": 12,
        "styles": {},
    }

    for index in range(0, 10):
        layout["items"].pop()

    layout["items"].append(col_3_id)
    layout["items"].append(col_2_id)
    layout["items"].append(col_1_id)

    context.blocks = blocks
    context.blocks_layout = layout
    context._p_changed = True


@onpath("/observatory/more-events-observatory")
def fix_observatory_eventsarchive(context):
    blocks = context.blocks
    layout = context.blocks_layout

    # remove the listing block
    last = context.blocks_layout["items"][-1]
    del blocks[last]
    context.blocks_layout["items"] = context.blocks_layout["items"][:-1]

    uid, block = make_events_archive_block()
    blocks[uid] = block
    layout["items"].append(uid)
    context._p_changed = True


@onpath("/observatory/news-archive-observatory")
def fix_observatory_newsarchive(context):
    blocks = context.blocks
    layout = context.blocks_layout
    uid = make_uid()
    block = {
        "@type": "listing",
        "block": uid,
        "headlineTag": "h2",
        "itemModel": {
            "@type": "item",
            "callToAction": {"label": "Read more"},
            "hasDate": True,
            "hasDescription": True,
            "hasEventDate": False,
            "hasIcon": False,
            "hasImage": False,
            "hasLink": True,
            "maxDescription": 2,
            "maxTitle": 2,
            "styles": {},
            "titleOnImage": False,
        },
        "query": [],
        "querystring": {
            "query": [
                {
                    "i": "include_in_observatory",
                    "o": "plone.app.querystring.operation.boolean.isTrue",
                    "v": "",
                },
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["News Item"],
                },
            ],
            "sort_on": "effective",
            "sort_order": "descending",
            "sort_order_boolean": True,
        },
        "styles": {},
        "variation": "summary",
    }
    blocks[uid] = block
    layout["items"].append(uid)
    context._p_changed = True


@onpath("/help/tutorial-videos/index_html")
def fix_tutorial_videos(context):
    blocks = context.blocks
    layout = context.blocks_layout

    videos = {
        1: {
            "text": {"id": layout["items"][-1], "block": blocks[layout["items"][-1]]},
            "video": {"id": layout["items"][-2], "block": blocks[layout["items"][-2]]},
        },
        2: {
            "text": {"id": layout["items"][-3], "block": blocks[layout["items"][-3]]},
            "video": {"id": layout["items"][-4], "block": blocks[layout["items"][-4]]},
        },
        3: {
            "text": {"id": layout["items"][-5], "block": blocks[layout["items"][-5]]},
            "video": {"id": layout["items"][-6], "block": blocks[layout["items"][-6]]},
        },
        4: {
            "text": {"id": layout["items"][-7], "block": blocks[layout["items"][-7]]},
            "video": {"id": layout["items"][-8], "block": blocks[layout["items"][-8]]},
        },
    }

    col_1_id = make_uid()
    col_1_item_1_id = make_uid()
    col_1_item_2_id = make_uid()

    col_2_id = make_uid()
    col_2_item_1_id = make_uid()
    col_2_item_2_id = make_uid()

    blocks[col_1_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_1_item_1_id: {
                    "blocks": {
                        videos[1]["video"]["id"]: videos[1]["video"]["block"],
                        videos[1]["text"]["id"]: videos[1]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[1]["video"]["id"],
                            videos[1]["text"]["id"],
                        ]
                    },
                },
                col_1_item_2_id: {
                    "blocks": {
                        videos[2]["video"]["id"]: videos[2]["video"]["block"],
                        videos[2]["text"]["id"]: videos[2]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[2]["video"]["id"],
                            videos[2]["text"]["id"],
                        ]
                    },
                },
            },
            "blocks_layout": {
                "items": [
                    col_1_item_2_id,
                    col_1_item_1_id,
                ]
            },
        },
        "gridCols": ["halfWidth", "halfWidth"],
        "gridSize": 12,
        "styles": {},
    }

    blocks[col_2_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_2_item_1_id: {
                    "blocks": {
                        videos[3]["video"]["id"]: videos[3]["video"]["block"],
                        videos[3]["text"]["id"]: videos[3]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[3]["video"]["id"],
                            videos[3]["text"]["id"],
                        ]
                    },
                },
                col_2_item_2_id: {
                    "blocks": {
                        videos[4]["video"]["id"]: videos[4]["video"]["block"],
                        videos[4]["text"]["id"]: videos[4]["text"]["block"],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[4]["video"]["id"],
                            videos[4]["text"]["id"],
                        ]
                    },
                },
            },
            "blocks_layout": {
                "items": [
                    col_2_item_2_id,
                    col_2_item_1_id,
                ]
            },
        },
        "gridCols": ["halfWidth", "halfWidth"],
        "gridSize": 12,
        "styles": {},
    }

    for index in range(0, 8):
        layout["items"].pop()

    layout["items"].append(col_2_id)
    layout["items"].append(col_1_id)

    context.blocks = blocks
    context.blocks_layout = layout
    context._p_changed = True


@onpath("/news-archive")
def fix_news_archive(context):
    current_lang = context.absolute_url(relative=True).split("/")[-2]

    listing_uid = make_uid()
    title_uid = make_uid()

    context.blocks = {
        title_uid: {"@type": "title", "hideContentType": True},
        listing_uid: {
            "@type": "listing",
            "headlineTag": "h2",
            "block": make_uid(),
            "itemModel": {
                "@type": "item",
                "hasDate": True,
                "hasDescription": True,
                "hasImage": False,
                "hasLink": True,
                "maxDescription": 2,
                "maxTitle": 2,
                "titleOnImage": False,
            },
            "query": [],
            "querystring": {
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": ["News Item", "Link"],
                    },
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": "/" + current_lang + "/news-archive",
                    },
                ],
                "sort_on": "effective",
                "sort_order": "descending",
                "sort_order_boolean": True,
            },
            "variation": "summary",
        },
    }

    context.blocks_layout = {"items": [title_uid, listing_uid]}
    context._p_changed = True


def fix_read_more(context):
    url = context.absolute_url(relative=True)

    PATHS = [
        "/knowledge/tools/urban-ast",
        "/knowledge/tools/adaptation-support-tool",
        "/knowledge/eu-vulnerability/eu-vulnerability-to-cc-impacts-occurring-outside",
        "/countries-regions/transnational-regions/baltic-sea-region/adaptation",
        "/countries-regions/transnational-regions/carpathian-mountains",
    ]

    def get_columns_block_id(blocks):
        columns_block = {k for k, v in blocks.items() if v["@type"] == "columnsBlock"}
        col_id = list(columns_block)[0]
        return col_id

    def get_read_more_block_id(blocks):
        read_more_block = {
            k for k, v in blocks.items() if v["@type"] == "readMoreBlock"
        }
        if read_more_block:
            read_more_block_id = list(read_more_block)[0]
            return read_more_block_id
        else:
            return None

    if are_in_path(url, SECTOR_POLICY_PATHS):
        col_id = get_block_id(context.blocks, "columnsBlock")
        col = context.blocks[col_id]
        first_col_id = col["data"]["blocks_layout"]["items"][0]
        first_col = col["data"]["blocks"][first_col_id]
        col_items = first_col["blocks_layout"]["items"]
        read_more_block_id = get_block_id(first_col["blocks"], "readMoreBlock")
        tiles = {
            k
            for k, v in first_col["blocks"].items()
            if v["@type"] == "relevantAceContent" or v["@type"] == "filterAceContent"
        }
        if read_more_block_id:
            read_more_index = col_items.index(read_more_block_id)
            col_items.pop(read_more_index)
            # insert before acecontent blocks
            col_items.insert(len(col_items) - len(tiles), read_more_block_id)
            first_col["blocks_layout"]["items"] = col_items

    elif are_in_path(url, PATHS):
        items = context.blocks_layout["items"]
        read_more_block_id = get_block_id(context.blocks, "readMoreBlock")
        if read_more_block_id:
            read_more_index = items.index(read_more_block_id)
            items.pop(read_more_index)
            # insert before last block
            items.insert(len(items) - 1, read_more_block_id)
            context.blocks_layout["items"] = items

    else:
        items = context.blocks_layout["items"]
        read_more_block_id = get_block_id(context.blocks, "readMoreBlock")
        if read_more_block_id:
            read_more_index = items.index(read_more_block_id)
            items.pop(read_more_index)
            items.append(read_more_block_id)  # insert as last one
            context.blocks_layout["items"] = items

    context._p_changed = True


def fix_images_in_slate(content):
    # for links like "resolveuid/231312"
    pass


def extract_first_column(context):
    # pull out the content from the column, we have a different layout for these pages
    title_block_id = context.blocks_layout["items"][0]
    title_block = context.blocks[title_block_id]

    if len(context.blocks_layout["items"]) == 1:
        # no content
        return

    column_block_id = context.blocks_layout["items"][1]
    column_block = context.blocks[column_block_id]

    if not column_block["@type"] == "columnsBlock":
        return

    second_column_id = column_block["data"]["blocks_layout"]["items"][1]
    second_column = column_block["data"]["blocks"][second_column_id]

    blocks = second_column["blocks"]
    blocks[title_block_id] = title_block

    context.blocks = second_column["blocks"]
    block_ids = [title_block_id] + second_column["blocks_layout"]["items"]
    context.blocks_layout = {"items": block_ids}


@inpath("knowledge/tools/urban-ast/")
def fix_uast(context):
    if not context.blocks:  # unmigrated content?
        return

    return extract_first_column(context)


@inpath("observatory/policy-context/country-profiles/")
def fix_obs_countries(context):
    # only for country profiles
    if not context.blocks:
        return

    if len(context.blocks) != 2:
        return

    last = context.blocks_layout["items"][-1:][0]
    block = context.blocks[last]
    if block.get("@type") != "columnsBlock":
        return

    context.subject = ("countryprofile",)
    context.reindexObject()

    # replace title block with special country header block
    for buid in context.blocks_layout["items"]:
        b = context.blocks[buid]
        if b.get("@type") == "title":
            country = get_country_alpha2(context.title)
            if country is not None:
                context.blocks[buid] = make_obs_countries_header(country)

    lastcoluid = block["data"]["blocks_layout"]["items"][-1]
    lastcol = block["data"]["blocks"][lastcoluid]

    listuid = lastcol["blocks_layout"]["items"][-1]
    listblock = lastcol["blocks"][listuid]
    listblock["querystring"]["query"][0]["v"] = ".."

    firstcoluid = block["data"]["blocks_layout"]["items"][0]
    # __import__("pdb").set_trace()
    firstcol = block["data"]["blocks"][firstcoluid]

    first_table_node_uid = None
    content_table_node_uid = None

    items = firstcol["blocks_layout"]["items"][:]

    slate_content = None

    # TODO: convert line images to image blocks
    for uid in items:
        block = firstcol["blocks"][uid]
        # TODO: remove empty paragraph block
        if block.get("@type") == "slate":
            value = block["value"] or []
            if not value:
                continue
            firstnode = block["value"][0]
            if isinstance(firstnode, dict) and firstnode.get("type") == "table":
                if not first_table_node_uid:
                    first_table_node_uid = uid
                    firstcol["blocks_layout"]["items"] = [x for x in items if x != uid]
                else:
                    tbody = firstnode["children"][0]
                    tr = tbody["children"][0]
                    slate_content = tr["children"][1]["children"]
                    content_table_node_uid = uid

    if slate_content:
        data = simple_slate_to_volto_blocks(slate_content)
        blocks = {}
        items = []
        for buid, b in data:
            blocks[buid] = b
            items.append(buid)
        firstcol["blocks"][content_table_node_uid] = {
            "@type": "group",
            "as": "div",
            "styles": {"style_name": None, "backgroundColor": "#e6e7e8"},
            "data": {"blocks": blocks, "blocks_layout": {"items": items}},
        }


@inpath("knowledge/tools/adaptation-support-tool")
def fix_ast(context):
    return extract_first_column(context)


def fix_layout_size(context):
    url = context.absolute_url(relative=True)

    page_blocks = context.blocks
    items = context.blocks_layout["items"]

    # skip this fix if a layoutSettings block already exists
    for block in page_blocks.values():
        if block.get("@type") == "layoutSettings":
            return

    # TODO: also handle narrow_view
    block = {"@type": "layoutSettings", "layout_size": "container_view"}
    block_uid = make_uid()
    page_blocks[block_uid] = block
    items = items[:1] + [block_uid] + items[1:]

    if are_on_path(url, FULL_PAGE_PATHS):
        block["layout_size"] = "wide_view"

    # if are_in_path(url, SECTOR_POLICY_PATHS):
    #     return
    #
    # if are_in_path(url, AST_PATHS):
    #     return

    context.blocks_layout["items"] = items
    context._p_changed = True


def fix_ast_header(context):
    obj = context
    url = obj.absolute_url(relative=True)

    if are_in_path(url, AST_PATHS):
        for tile in obj.list_tiles():
            if "ast_header" in obj.get_tile_type(tile):
                tile = obj.get_tile(tile)
                tile_dm = ITileDataManager(tile)
                data = tile_dm.get()
                title = data.get("title")
                step = data.get("step")
                title_block_id = get_block_id(obj.blocks, "title")
                subtitle = str(step) + ". " + title
                new_data = {
                    "@type": "title",
                    "hideContentType": True,
                    "subtitle": subtitle,
                }
                obj.blocks[title_block_id] = new_data
                obj.title = subtitle

        for tile in obj.list_tiles():
            if "richtext_with_title" in obj.get_tile_type(tile):
                tile = obj.get_tile(tile)
                tile_dm = ITileDataManager(tile)
                data = tile_dm.get()
                title = data.get("title")
                if title and title[:1].isdigit():
                    obj.title = title

        title_block_id = get_block_id(obj.blocks, "title")
        if "subtitle" not in obj.blocks[title_block_id]:
            obj.blocks[title_block_id]["subtitle"] = ""

        if obj.blocks[title_block_id]["subtitle"] == obj.title:
            obj.blocks[title_block_id]["subtitle"] = ""

    obj._p_changed = True


def fix_field_encoding(context):
    title = context.title
    if isinstance(title, str):
        title = title.decode("utf-8")
        context.title = title

    description = context.description
    if isinstance(description, str):
        description = description.decode("utf-8")
        context.description = description


@inpath("countries-regions/transnational-regions/")
def fix_preview_image(context):
    folder_images = context.listFolderContents(contentFilter={"portal_type": "Image"})
    folder_image = None
    if len(folder_images) > 0:
        folder_image = folder_images[0]
    if folder_image:
        image = folder_image.image
        context.preview_image = image
        context._p_changed = True


def getpath(obj):
    return "/" + obj.absolute_url(relative=1)


def exclude(obj):
    obj.exclude_from_nav = True
    obj.reindexObject()  # update_metadata=True - only on p6


def include(obj):
    obj.exclude_from_nav = False
    obj.reindexObject()  # update_metadata=True - only on p6


def is_top_level_path(path):
    for test_path in TOP_LEVEL:
        if path == test_path or path == "/cca" + test_path:
            return True
    return False


def exclude_content_from_navigation(site):
    main = site.restrictedTraverse("en")
    for oid, obj in main.contentItems():
        path = getpath(obj)
        if not is_top_level_path(path):
            exclude(obj)

            logger.debug("Excluded from nav: %s", path)

            intl_mgr = get_translation_manager(obj)
            for lang in languages:
                trans = intl_mgr.get_translation(lang)

                if trans is None:
                    continue

                exclude(trans)
                logger.debug("Excluded from nav: %s", getpath(trans))
        else:
            include(obj)

            # children
            # for child_path in top_level[path]:
            #     child = obj[child_path]
            #     exclude(child)


site_fixers = [exclude_content_from_navigation]

content_fixers = [
    fix_field_encoding,
    fix_images_in_slate,
    fix_climate_services_toc,
    fix_tutorial_videos,
    fix_vibiomapviewer,
    fix_uast,
    fix_ast,
    fix_webinars,
    fix_read_more,
    fix_ast_header,
    fix_obs_countries,
    fix_layout_size,
]

folder_fixers = [
    fix_field_encoding,
    fix_news_archive,
    fix_preview_image,
    fix_observatory_newsarchive,
    fix_observatory_eventsarchive,
    fix_layout_size,
]


def fix_content(content):
    for fixer in content_fixers:
        fixer(content)


def fix_folder(context):
    for fixer in folder_fixers:
        fixer(context)


def fix_site(site):
    for fixer in site_fixers:
        fixer(site)
