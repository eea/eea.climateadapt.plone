"""Post-migration "fixers", which are executed after an object has been migrated"""

import logging

from eea.climateadapt.interfaces import ICCACountry
from plone.api import portal
from plone.app.multilingual.api import get_translation_manager
from plone.namedfile.file import NamedBlobImage
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
    """returns true if object path ends with this path"""

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
    block = {k for k, v in list(blocks.items()) if v["@type"] == type}
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


@inpath("/observatory/evidence/health-effects")
def fix_health_effects(context):
    # fixes the first columns block that has two images side by side
    for block in list(context.blocks.values()):
        if block["@type"] == "columnsBlock":
            block["gridCols"] = ["fourFifths", "oneFifth"]
            sec_col_uid = block["data"]["blocks_layout"]["items"][-1]
            sec_col = block["data"]["blocks"][sec_col_uid]
            for imgblock in list(sec_col["blocks"].values()):
                if imgblock["@type"] == "image":
                    imgblock["align"] = "center"
                    imgblock["size"] = "l"
            context._p_changed = True


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


@onpath("/newsletter")
def fix_newsletter(context):
    def get_year(text, years):
        """Extract the year: MARCH 2023 -> 2023"""
        for year in years:
            if str(year) in str(text):
                return year
        return None

    # 1. Extract the list of td items containing the newsletters
    blocks = context.blocks
    res_blocks = []
    for k in list(blocks.keys()):
        res_blocks.append(blocks[k])

    years = [x for x in reversed(list(range(2015, 2024)))]
    res_tables = [x["value"] for x in res_blocks if "url" in str(x)]

    res = []
    for table in res_tables:
        tbody = table[0]["children"][0]
        row = tbody["children"][0]
        data = row["children"]

        for item in data:
            newsletter = item["children"][0]
            res.append(newsletter)

    newsletters_data = []
    filtered_res = [x for x in res if "url" in str(x)]

    # 2. Extract relevant info for each newsletter item
    for newsletter_item in filtered_res:
        n_data = {}
        newsletter_url = newsletter_item["data"]["url"]
        n_data["url"] = newsletter_url
        # newsletter_info = newsletter_item['children']
        # n_data['info'] = newsletter_info

        for child in newsletter_item["children"]:
            if "text" in list(child.keys()):
                if "Issue" in child["text"]:
                    newsletter_title = child["text"]
                    n_data["title"] = newsletter_title
                else:
                    year = get_year(child, years)
                    if year is not None:
                        n_data["date_title"] = child["text"]
                        n_data["year"] = year

            if "scale" in list(child.keys()):
                if "url" in list(child.keys()):
                    img_url = child["url"]
                    n_data["img_url"] = img_url

        newsletters_data.append(n_data)

    # 3. Group newsletters by year
    n_by_year = {}
    for year in years:
        n_by_year[year] = []
    for n_item in newsletters_data:
        n_by_year[n_item["year"]].append(n_item)

    # TODO: 4. Generate nice listing blocks using the prepared information
    # __import__('pdb').set_trace()

    # "18354c46-7412-4362-92a0-06ba1a568431": {
    #   "@type": "imagecards",
    #   "align": "left",
    #   "cards": [
    #     {
    #       "@id": "a423c8a7-e985-435e-b547-3c17c18829ee",
    #       "attachedimage": "http://localhost:3000/newsletter/river-219972_1280.jpg",
    #       "link": "http://localhost:3000/sandbox",
    #       "text": [
    #         {
    #           "children": [
    #             {
    #               "text": "Text aici"
    #             }
    #           ],
    #           "type": "p"
    #         }
    #       ],
    #       "title": "Titlu aici"
    #     },
    #     {
    #       "@id": "78c4d186-962e-4352-bc37-a38a94bc57e1",
    #       ...
    #     }
    #   ],
    #   "display": "round_tiled",
    #   "image_scale": "large"
    # },


def fix_read_more(context):
    url = context.absolute_url(relative=True)

    PATHS = [
        "/knowledge/tools/urban-ast",
        "/knowledge/tools/adaptation-support-tool",
        "/knowledge/eu-vulnerability/eu-vulnerability-to-cc-impacts-occurring-outside",
        "/countries-regions/transnational-regions/baltic-sea-region/adaptation",
        "/countries-regions/transnational-regions/carpathian-mountains",
    ]

    if are_in_path(url, SECTOR_POLICY_PATHS):
        col_id = get_block_id(context.blocks, "columnsBlock")
        col = context.blocks[col_id]
        first_col_id = col["data"]["blocks_layout"]["items"][0]
        first_col = col["data"]["blocks"][first_col_id]
        col_items = first_col["blocks_layout"]["items"]
        read_more_block_id = get_block_id(first_col["blocks"], "readMoreBlock")
        tiles = {
            k
            for k, v in list(first_col["blocks"].items())
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


@inpath("/countries-regions/countries/")
def fix_cca_countries(context):
    if not ICCACountry.providedBy(context):
        return

    # remove the title block
    uid = None
    disclaimer_block = None
    for k, v in list(context.blocks.items()):
        if v.get("@type") == "title":
            uid = k
        if v.get("@type") == "slate":
            disclaimer_block = k

    uids = [uid, disclaimer_block]

    # move the disclaimer block to be the last
    context.blocks_layout["items"] = [
        x for x in context.blocks_layout["items"] if x not in uids
    ] + (disclaimer_block and [disclaimer_block] or [])

    _types = [block["@type"] for block in list(context.blocks.values())]

    if "countryProfileDetail" not in _types:
        # these are the Turkey, Norway and...
        # delete all slate blocks that are not disclaimer
        todelete = []

        for uid in context.blocks_layout["items"]:
            block = context.blocks[uid]
            if block["@type"] not in ["slate", "tabs_block"]:
                continue
            if "Last update" not in block.get("plaintext", ""):
                todelete.append(uid)

        for uid in todelete:
            del context.blocks[uid]
        context.blocks_layout["items"] = [
            uid for uid in context.blocks_layout["items"] if uid not in todelete
        ]
        uid = make_uid()
        block = {"@type": "countryProfileDetail"}
        context.blocks_layout["items"].insert(
            len(context.blocks_layout["items"]) - 2, uid
        )
        context.blocks[uid] = block
        logger.info("Fixed country profile without countryProfileDetail")

    context._p_changed = True


@inpath("observatory/policy-context/country-profiles/")
def fix_obs_countries(context):
    # only for country profiles
    if not context.blocks:
        return

    if len(context.blocks) != 2:
        return

    lastuid = context.blocks_layout["items"][-1:][0]
    mainblock = context.blocks[lastuid]
    if mainblock.get("@type") != "columnsBlock":
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

    # __import__("pdb").set_trace()
    # lastcoluid = block["data"]["blocks_layout"]["items"][-1]
    # lastcol = block["data"]["blocks"][lastcoluid]
    # listuid = lastcol["blocks_layout"]["items"][-1]
    # listblock = lastcol["blocks"][listuid]
    # listblock["querystring"]["query"][0]["v"] = ".."

    firstcoluid = mainblock["data"]["blocks_layout"]["items"][0]
    firstcol = mainblock["data"]["blocks"][firstcoluid]

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

    # replace the column with the content of the column
    # context.blocks[firstcoluid] = firstcol
    context.blocks_layout["items"] = context.blocks_layout["items"][:-1]

    uids = firstcol["blocks_layout"]["items"][:]
    context.blocks_layout["items"] += uids
    for uid in uids:
        context.blocks[uid] = firstcol["blocks"][uid]

    del context.blocks[lastuid]


@inpath("knowledge/tools/adaptation-support-tool")
def fix_ast(context):
    return extract_first_column(context)


def fix_layout_size(context):
    url = context.absolute_url(relative=True)

    page_blocks = context.blocks
    items = context.blocks_layout["items"]

    # skip this fix if a layoutSettings block already exists
    for block in list(page_blocks.values()):
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

    def migrate_ast_header(obj):
        title_block_id = get_block_id(obj.blocks, "title")
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
                    "subtitle": subtitle if step != 0 else title,
                }
                obj.blocks[title_block_id] = new_data
                if step == 0:
                    obj.title = title
                else:
                    obj.title = subtitle

        for tile in obj.list_tiles():
            if "richtext_with_title" in obj.get_tile_type(tile):
                tile = obj.get_tile(tile)
                tile_dm = ITileDataManager(tile)
                data = tile_dm.get()
                strip = data.get("dont_strip")
                title = data.get("title")
                if title:
                    if title[:1].isdigit() or strip == True:
                        obj.title = title

        if "subtitle" not in obj.blocks[title_block_id]:
            obj.blocks[title_block_id]["subtitle"] = ""

        if obj.blocks[title_block_id]["subtitle"] == obj.title:
            obj.blocks[title_block_id]["subtitle"] = ""

    if are_in_path(url, AST_PATHS):
        if hasattr(obj, "list_tiles"):
            migrate_ast_header(obj)

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


def fix_c3s_indicators_listing(context):
    # adds the c3sIndicatorListing block
    uid = make_uid()
    context.blocks_layout["items"].append(uid)
    context.blocks[uid] = {"@type": "c3SIndicatorListingBlock"}

    topic = context.getId()
    img_map = {
        "agriculture": "img-agriculture.jpg",
        "energy": "img-energy.jpg",
        "health": "img-health.jpg",
        "forestry": "img-forestry.jpg",
        "tourism": "img-tourism.jpg",
        "water-and-coastal": "img-coastal.jpg",
    }
    img_name = img_map.get(topic)
    if img_name:
        site = portal.get()
        base_folder = site.restrictedTraverse("en/knowledge/c3sdataimg")
        if img_name in base_folder.contentIds():
            img = base_folder.restrictedTraverse(img_name)
            field = img.image
            if field:
                data = field.open().read()
                context.preview_image = NamedBlobImage(
                    data=data, contentType=field.contentType, filename=field.filename
                )

    context._p_changed = True


pagelayout_fixers = {"c3s_indicators_listing": fix_c3s_indicators_listing}


def fix_for_pagelayout(context):
    layout = getattr(context.aq_inner.aq_self, "layout", None)
    if layout:
        fixer = pagelayout_fixers.get(layout)
        if fixer:
            fixer(context)


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
    fix_health_effects,
    fix_uast,
    fix_ast,
    fix_webinars,
    fix_read_more,
    fix_ast_header,
    fix_obs_countries,
    fix_layout_size,
    fix_newsletter,
    fix_for_pagelayout,
    fix_cca_countries,
]

folder_fixers = [
    fix_field_encoding,
    fix_news_archive,
    fix_preview_image,
    fix_observatory_newsarchive,
    fix_observatory_eventsarchive,
    fix_layout_size,
    fix_for_pagelayout,
    fix_cca_countries,
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
