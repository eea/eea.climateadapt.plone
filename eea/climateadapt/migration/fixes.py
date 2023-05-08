""" Post-migration "fixers", which are executed after an object has been migrated
"""


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
