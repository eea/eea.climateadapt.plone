""" Post-migration "fixers", which are executed after an object has been migrated
"""


import logging

from plone.app.multilingual.api import get_translation_manager
from eea.climateadapt.translation.utils import get_current_language
from .config import LANGUAGES, TOP_LEVEL
from .utils import make_uid

logger = logging.getLogger()


def fix_climate_services_toc(context):
    # TODO: make multilingual aware

    # in first column block, replace the first paragraph with a horizontal navigation table of contents

    path = 'cca/en/knowledge/adaptation-information/climate-services/climate-services'

    if context.absolute_url(relative=True) != path:
        return

    col_block_id = context.blocks_layout['items'][1]    # [0] is title block
    col = context.blocks[col_block_id]
    column_ids = col['data']['blocks_layout']['items']
    first_col_id = column_ids[0]
    first_col = col['data']['blocks'][first_col_id]

    first_block_id = first_col['blocks_layout']['items'][0]
    new_data = {"@type": 'toc',
                "variation": "horizontalMenu"}
    first_col['blocks'][first_block_id] = new_data

def fix_news_archive(context, request):
    current_lang = get_current_language(context, request)
    path = 'cca/' + current_lang + '/news-archive'

    if context.absolute_url(relative=True) != path:
        return

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
                "hasDescription":True,
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


fixers = [fix_climate_services_toc]
folder_fixers = [fix_news_archive]


def fix_content(content):
    for fixer in fixers:
        fixer(content)

def fix_folder(context, request):
    for fixer in folder_fixers:
        fixer(context, request)


languages = [lang for lang in LANGUAGES if lang != 'en']


def getpath(obj):
    return "/" + obj.absolute_url(relative=1)


def exclude(obj):
    obj.exclude_from_nav = True
    obj.reindexObject()     # update_metadata=True - only on p6


def include(obj):
    obj.exclude_from_nav = False
    obj.reindexObject()     # update_metadata=True - only on p6


def exclude_content_from_navigation(site):
    main = site.restrictedTraverse('en')
    for oid, obj in main.contentItems():
        path = getpath(obj)
        if path not in TOP_LEVEL:
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
