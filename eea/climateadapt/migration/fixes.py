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


def fix_tutorial_videos(context, request):
    current_lang = get_current_language(context, request)
    path = 'cca/' + current_lang + '/help/tutorial-videos'

    if context.absolute_url(relative=True) != path:
        return

    # prepare video blocks
    video_1_uid = make_uid()
    video_2_uid = make_uid()
    video_3_uid = make_uid()
    video_4_uid = make_uid()
    videos = {
        video_1_uid: {
            "@type": "nextCloudVideo",
            "url": 'https://cmshare.eea.europa.eu/s/KbaSFnSGyQZra5L/download',
            "title": '',
        },
        video_2_uid: {
            "@type": "nextCloudVideo",
            "url": 'https://cmshare.eea.europa.eu/s/7XiT5R6miLTXXFt/download',
            "title": '',
        },
        video_3_uid: {
            "@type": "nextCloudVideo",
            "url": 'https://cmshare.eea.europa.eu/s/wRWfQsPzREXWrwn/download',
            "title": '',
        },
        video_4_uid: {
            "@type": "nextCloudVideo",
            "url": 'https://cmshare.eea.europa.eu/s/sYPnWgfNDHeeSKR/download',
            "title": '',
        }
    }

    blocks = context.blocks
    blocks[video_1_uid] = videos[video_1_uid]
    blocks[video_2_uid] = videos[video_2_uid]
    blocks[video_3_uid] = videos[video_3_uid]
    blocks[video_4_uid] = videos[video_4_uid]

    # prepare texts for videos
    layout = context.blocks_layout
    video_1_text = layout['items'][-4]
    video_2_text = layout['items'][-3]
    video_3_text = layout['items'][-2]
    video_4_text = layout['items'][-1]
    layout['items'].pop()
    layout['items'].pop()
    layout['items'].pop()
    layout['items'].pop()

    # add videos and texts
    layout['items'].append(video_1_uid)
    layout['items'].append(video_1_text)
    layout['items'].append(video_2_uid)
    layout['items'].append(video_2_text)
    layout['items'].append(video_3_uid)
    layout['items'].append(video_3_text)
    layout['items'].append(video_4_uid)
    layout['items'].append(video_4_text)

    context.blocks = blocks
    context.blocks_layout = layout
    context._p_changed = True


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


fixers = [fix_climate_services_toc]
folder_fixers = [fix_news_archive, fix_tutorial_videos]


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
