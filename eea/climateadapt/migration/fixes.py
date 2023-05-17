""" Post-migration "fixers", which are executed after an object has been migrated
"""


import logging

from plone.app.multilingual.api import get_translation_manager

logger = logging.getLogger()


def fix_climate_services_toc(context):
    # TODO: make multilingual aware

    # in first column block, replace the first paragraph with a horizontal navigation table of contents

    path = 'cca/en/knowledge/adaptation-information/climate-services/climate-services'

    if context.absolute_url(relative=True) != path:
        return

    col_block_id = context.blocks_layout['items'][0]
    col = context.blocks[col_block_id]
    column_ids = col['data']['blocks_layout']['items']
    first_col_id = column_ids[0]
    first_col = col['data']['blocks'][first_col_id]

    first_block_id = first_col['blocks_layout']['items'][0]
    new_data = {"@type": 'toc',
                "variation": "horizontalMenu"}
    first_col['blocks'][first_block_id] = new_data


fixers = [fix_climate_services_toc]


def fix_content(content):
    for fixer in fixers:
        fixer(content)


languages = ['de', 'fr', 'es', 'it', 'pl']

top_level = {
    '/cca/en/about': [],
    '/cca/en/eu-adaptation-policy': [],
    '/cca/en/countries-regions': [],
    '/cca/en/knowledge': [],
    '/cca/en/network': [],
}


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
        if path not in top_level:
            exclude(obj)

            logger.info("Excluded from nav: %s", path)

            intl_mgr = get_translation_manager(obj)
            for lang in languages:
                trans = intl_mgr.get_translation(lang)

                if trans is None:
                    continue

                exclude(trans)
                logger.info("Excluded from nav: %s", getpath(trans))
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
