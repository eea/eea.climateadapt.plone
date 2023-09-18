IGNORED_CONTENT_TYPES = [
    # TODO:
    # 'Document',
    'Event',
    'News Item',
    'cca-event',

    'eea.climateadapt.aceproject',
    'eea.climateadapt.adaptationoption',
    'eea.climateadapt.c3sindicator',
    'eea.climateadapt.casestudy',
    'eea.climateadapt.city_profile',
    'eea.climateadapt.guidancedocument',
    'eea.climateadapt.indicator',
    'eea.climateadapt.informationportal',
    'eea.climateadapt.mapgraphdataset',
    'eea.climateadapt.organisation',
    'eea.climateadapt.publicationreport',
    'eea.climateadapt.researchproject',
    'eea.climateadapt.tool',
    'eea.climateadapt.video',

    'Image', 'LRF', 'LIF', 'Collection', 'Link', 'DepictionTool', 'Subsite',
    'File',
    'eea.climateadapt.city_profile',
    'FrontpageSlide',
    'EasyForm'

]

LANGUAGES = ['de', 'fr', 'es', 'it', 'pl', 'en']


IGNORED_PATHS = [
    '{lang}/mission',
    '{lang}/metadata'
    'frontpage',
    '{lang}/frontpage',
    '{lang}/observatory/news-archive-observatory',
]

COL_MAPPING = {
    2: 'oneThird',
    3: 'oneThird',
    4: 'oneThird',
    5: 'oneThird',
    6: 'halfWidth',
    7: 'twoThirds',
    8: 'twoThirds',
    9: 'twoThirds',
    10: 'twoThirds',
    12: 'full',
}

TOP_LEVEL = {
    '/en/about': [],
    '/en/eu-adaptation-policy': [],
    '/en/countries-regions': [],
    '/en/knowledge': [],
    '/en/network': [],
}

AST_PATHS = [
    '/knowledge/tools/urban-ast',
    '/knowledge/tools/adaptation-support-tool'
]

FULL_PAGE_PATHS = [
    '/observatory',
    '/knowledge/forestry'
]

