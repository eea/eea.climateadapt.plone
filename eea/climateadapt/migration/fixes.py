""" Post-migration "fixers", which are executed after an object has been migrated
"""


import logging

from plone.app.multilingual.api import get_translation_manager

from .config import LANGUAGES, TOP_LEVEL, AST_PATHS, FULL_PAGE_PATHS
from .utils import make_uid

logger = logging.getLogger()


def onpath(path):

    def decorator_factory(func):
        def decorator(context):
            if not context.absolute_url(relative=True).endswith(path):
                return
            return func(context)

        return decorator

    return decorator_factory


def inpath(path):

    def decorator_factory(func):
        def decorator(context):
            if path not in context.absolute_url(relative=True):
                return
            return func(context)

        return decorator

    return decorator_factory


@onpath('/knowledge/adaptation-information/climate-services/climate-services')
def fix_climate_services_toc(context):
    # in first column block, replace the first paragraph with a horizontal navigation table of contents

    col_block_id = context.blocks_layout['items'][1]    # [0] is title block
    col = context.blocks[col_block_id]
    column_ids = col['data']['blocks_layout']['items']
    first_col_id = column_ids[0]
    first_col = col['data']['blocks'][first_col_id]

    first_block_id = first_col['blocks_layout']['items'][0]
    new_data = {"@type": 'toc',
                "variation": "horizontalMenu"}
    first_col['blocks'][first_block_id] = new_data


@onpath('/help/Webinars')
def fix_webinars(context):
    blocks = context.blocks
    layout = context.blocks_layout

    videos = {
        1:  {
            'text': {
                'id': layout['items'][-1],
                'block': blocks[layout['items'][-1]]
            },
            'video': {
                'id': layout['items'][-2],
                'block': blocks[layout['items'][-2]]
            }
        },
        2:  {
            'text': {
                'id': layout['items'][-3],
                'block': blocks[layout['items'][-3]]
            },
            'video': {
                'id': layout['items'][-4],
                'block': blocks[layout['items'][-4]]
            }
        },
        3:  {
            'text': {
                'id': layout['items'][-5],
                'block': blocks[layout['items'][-5]]
            },
            'video': {
                'id': layout['items'][-6],
                'block': blocks[layout['items'][-6]]
            }
        },
        4:  {
            'text': {
                'id': layout['items'][-7],
                'block': blocks[layout['items'][-7]]
            },
            'video': {
                'id': layout['items'][-8],
                'block': blocks[layout['items'][-8]]
            }
        },
        5:  {
            'text': {
                'id': layout['items'][-9],
                'block': blocks[layout['items'][-9]]
            },
            'video': {
                'id': layout['items'][-10],
                'block': blocks[layout['items'][-10]]
            }
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
                        videos[1]['video']['id']: videos[1]['video']['block'],
                        videos[1]['text']['id']: videos[1]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[1]['video']['id'],
                            videos[1]['text']['id'],
                        ]
                    }
                },
            },
            "blocks_layout": {
                "items": [
                    col_1_item_1_id,
                ]
            }
        },
        "gridCols": [
            "halfWidth",
            "halfWidth"
        ],
        "gridSize": 12,
        "styles": {}
    }

    blocks[col_2_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_2_item_1_id: {
                    "blocks": {
                        videos[2]['video']['id']: videos[2]['video']['block'],
                        videos[2]['text']['id']: videos[2]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[2]['video']['id'],
                            videos[2]['text']['id'],
                        ]
                    }
                },
                col_2_item_2_id: {
                    "blocks": {
                        videos[3]['video']['id']: videos[3]['video']['block'],
                        videos[3]['text']['id']: videos[3]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[3]['video']['id'],
                            videos[3]['text']['id'],
                        ]
                    }
                },
            },
            "blocks_layout": {
                "items": [
                    col_2_item_2_id,
                    col_2_item_1_id,
                ]
            }
        },
        "gridCols": [
            "halfWidth",
            "halfWidth"
        ],
        "gridSize": 12,
        "styles": {}
    }

    blocks[col_3_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_3_item_1_id: {
                    "blocks": {
                        videos[4]['video']['id']: videos[4]['video']['block'],
                        videos[4]['text']['id']: videos[4]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[4]['video']['id'],
                            videos[4]['text']['id'],
                        ]
                    }
                },
                col_3_item_2_id: {
                    "blocks": {
                        videos[5]['video']['id']: videos[5]['video']['block'],
                        videos[5]['text']['id']: videos[5]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[5]['video']['id'],
                            videos[5]['text']['id'],
                        ]
                    }
                },
            },
            "blocks_layout": {
                "items": [
                    col_3_item_2_id,
                    col_3_item_1_id,
                ]
            }
        },
        "gridCols": [
            "halfWidth",
            "halfWidth"
        ],
        "gridSize": 12,
        "styles": {}
    }

    for index in range(0, 10):
        layout['items'].pop()

    layout['items'].append(col_3_id)
    layout['items'].append(col_2_id)
    layout['items'].append(col_1_id)

    context.blocks = blocks
    context.blocks_layout = layout
    context._p_changed = True


@onpath('/help/tutorial-videos/index_html')
def fix_tutorial_videos(context):
    blocks = context.blocks
    layout = context.blocks_layout

    videos = {
        1:  {
            'text': {
                'id': layout['items'][-1],
                'block': blocks[layout['items'][-1]]
            },
            'video': {
                'id': layout['items'][-2],
                'block': blocks[layout['items'][-2]]
            }
        },
        2:  {
            'text': {
                'id': layout['items'][-3],
                'block': blocks[layout['items'][-3]]
            },
            'video': {
                'id': layout['items'][-4],
                'block': blocks[layout['items'][-4]]
            }
        },
        3:  {
            'text': {
                'id': layout['items'][-5],
                'block': blocks[layout['items'][-5]]
            },
            'video': {
                'id': layout['items'][-6],
                'block': blocks[layout['items'][-6]]
            }
        },
        4:  {
            'text': {
                'id': layout['items'][-7],
                'block': blocks[layout['items'][-7]]
            },
            'video': {
                'id': layout['items'][-8],
                'block': blocks[layout['items'][-8]]
            }
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
                        videos[1]['video']['id']: videos[1]['video']['block'],
                        videos[1]['text']['id']: videos[1]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[1]['video']['id'],
                            videos[1]['text']['id'],
                        ]
                    }
                },
                col_1_item_2_id: {
                    "blocks": {
                        videos[2]['video']['id']: videos[2]['video']['block'],
                        videos[2]['text']['id']: videos[2]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[2]['video']['id'],
                            videos[2]['text']['id'],
                        ]
                    }
                },
            },
            "blocks_layout": {
                "items": [
                    col_1_item_2_id,
                    col_1_item_1_id,
                ]
            }
        },
        "gridCols": [
            "halfWidth",
            "halfWidth"
        ],
        "gridSize": 12,
        "styles": {}
    }

    blocks[col_2_id] = {
        "@type": "columnsBlock",
        "data": {
            "blocks": {
                col_2_item_1_id: {
                    "blocks": {
                        videos[3]['video']['id']: videos[3]['video']['block'],
                        videos[3]['text']['id']: videos[3]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[3]['video']['id'],
                            videos[3]['text']['id'],
                        ]
                    }
                },
                col_2_item_2_id: {
                    "blocks": {
                        videos[4]['video']['id']: videos[4]['video']['block'],
                        videos[4]['text']['id']: videos[4]['text']['block'],
                    },
                    "blocks_layout": {
                        "items": [
                            videos[4]['video']['id'],
                            videos[4]['text']['id'],
                        ]
                    }
                },
            },
            "blocks_layout": {
                "items": [
                    col_2_item_2_id,
                    col_2_item_1_id,
                ]
            }
        },
        "gridCols": [
            "halfWidth",
            "halfWidth"
        ],
        "gridSize": 12,
        "styles": {}
    }

    for index in range(0, 8):
        layout['items'].pop()

    layout['items'].append(col_2_id)
    layout['items'].append(col_1_id)

    context.blocks = blocks
    context.blocks_layout = layout
    context._p_changed = True


@onpath('/news-archive')
def fix_news_archive(context):

    current_lang = context.absolute_url(relative=True).split('/')[-2]

    listing_uid = make_uid()
    title_uid = make_uid()

    context.blocks = {
        title_uid: {"@type": "title"},
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
                "titleOnImage": False
            },
            "query": [],
            "querystring": {
                "query": [
                    {
                        "i": "portal_type",
                        "o": "plone.app.querystring.operation.selection.any",
                        "v": [
                            "News Item",
                            "Link"
                        ]
                    },
                    {
                        "i": "path",
                        "o": "plone.app.querystring.operation.string.absolutePath",
                        "v": "/" + current_lang + "/news-archive"
                    }
                ],
                "sort_on": "effective",
                "sort_order": "descending",
                "sort_order_boolean": True
            },
            "variation": "summary"
        }
    }

    context.blocks_layout = {"items": [title_uid, listing_uid]}
    context._p_changed = True


def fix_images_in_slate(content):
    # for links like "resolveuid/231312"
    pass


def extract_first_column(context):
    # pull out the content from the column, we have a different layout for these pages
    title_block_id = context.blocks_layout['items'][0]
    title_block = context.blocks[title_block_id]

    if len(context.blocks_layout['items']) == 1:
        # no content
        return

    column_block_id = context.blocks_layout['items'][1]
    column_block = context.blocks[column_block_id]

    if not column_block['@type'] == 'columnsBlock':
        return

    second_column_id = column_block['data']['blocks_layout']['items'][1]
    second_column = column_block['data']['blocks'][second_column_id]

    blocks = second_column['blocks']
    blocks[title_block_id] = title_block

    context.blocks = second_column['blocks']
    block_ids = [title_block_id] + second_column['blocks_layout']['items']
    context.blocks_layout = {"items": block_ids}


@inpath('knowledge/tools/urban-ast/')
def fix_uast(context):

    if not context.blocks:  # unmigrated content?
        return

    return extract_first_column(context)


@inpath('knowledge/tools/adaptation-support-tool')
def fix_ast(context):
    return extract_first_column(context)


def is_full_layout_path(url):
    for path in FULL_PAGE_PATHS:
        if url.endswith(path):
            return True
        
def is_ast_path(url):
    for path in AST_PATHS:
        if path in url:
            return True

def fix_layout_size(context):
    url = context.absolute_url(relative=True)

    if is_ast_path(url):
        return

    if is_full_layout_path(url):
        return

    layout_uid = make_uid()
    page_blocks = context.blocks
    page_blocks_layout = context.blocks_layout
    uids = page_blocks_layout['items'] + [layout_uid]
    blocks_layout = {"items":  uids}
    _blocks = {}
    _blocks[layout_uid] = {"@type": "layoutSettings", "layout_size": "narrow_view"}
   
    for (uid, block) in page_blocks.items():
        _blocks[uid] = block
   
    context.blocks = _blocks
    context.blocks_layout = blocks_layout
    context._p_changed = True


def fix_field_encoding(context):

    title = context.title
    if isinstance(title, str):
        title = title.decode('utf-8')
        context.title = title

    description = context.description
    if isinstance(description, str):
        description = description.decode('utf-8')
        context.description = description


content_fixers = [fix_field_encoding, fix_images_in_slate,
                  fix_climate_services_toc, fix_tutorial_videos, fix_uast,
                  fix_ast, fix_webinars]
folder_fixers = [fix_field_encoding, fix_news_archive]


def fix_content(content):
    for fixer in content_fixers:
        fixer(content)


def fix_folder(context):
    for fixer in folder_fixers:
        fixer(context)


languages = [lang for lang in LANGUAGES if lang != 'en']


def getpath(obj):
    return "/" + obj.absolute_url(relative=1)


def exclude(obj):
    obj.exclude_from_nav = True
    obj.reindexObject()     # update_metadata=True - only on p6


def include(obj):
    obj.exclude_from_nav = False
    obj.reindexObject()     # update_metadata=True - only on p6


def is_top_level_path(path):
    for test_path in TOP_LEVEL:
        if path == test_path or path == '/cca' + test_path:
            return True
    return False


def exclude_content_from_navigation(site):
    main = site.restrictedTraverse('en')
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


site_fixers = [
    exclude_content_from_navigation
]


def fix_site(site):
    for fixer in site_fixers:
        fixer(site)
