import logging

from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from eea.climateadapt.interfaces import ITransnationalRegionMarker
from eea.climateadapt.translation.utils import get_current_language, translated_url

logger = logging.getLogger("eea.climateadapt")

regions = {
    "Adriatic-Ionian": [
        [
            ("Croatia", "/countries/croatia"),
            ("Greece", "/countries/greece"),
            ("Italy", "/countries/italy"),
            ("Slovenia", "/countries/slovenia"),
            ("Albania", ""),
            ("Bosnia and Herzegovina", ""),
            ("Montenegro", ""),
            ("Republic of North Macedonia", ""),
            ("Serbia", ""),
        ],
        [("adriatic _ionian.jpg")],
    ],
    "Alpine Space": [
        [
            ("Austria", "/countries/austria"),
            ("France", "/countries/france"),
            ("Germany", "/countries/germany"),
            ("Italy", "/countries/italy"),
            ("Slovenia", "/countries/slovenia"),
            ("Liechtenstein", ""),
            ("Switzerland", "/countries/switzerland"),
        ],
        [("alpine_space.jpg")],
    ],
    "Northern Periphery and Artic": [
        [
            ("Finland", "/countries/finland"),
            ("Ireland", "/countries/ireland"),
            ("Sweden", "/countries/sweden"),
            # ('United Kingdom', '/countries/united-kingdom'),
            ("Iceland", "/countries/iceland"),
            ("Norway", "/countries/norway"),
            ("Greenland", ""),
            ("Faroe Islands", ""),
        ],
        [("northern_periphery_and_arctic.jpg")],
    ],
    "Atlantic": [
        [
            ("France", "/countries/france"),
            ("Ireland", "/countries/ireland"),
            ("Portugal", "/countries/portugal"),
            ("Spain", "/countries/spain"),
            # ('United Kingdom', '/countries/united-kingdom')
        ],
        [("atlantic_area.jpg")],
    ],
    # 'Balkan-Mediterranean': [
    #    [('Bulgaria', '/countries/bulgaria'),
    #     ('Cyprus', '/countries/cyprus'),
    #     ('Greece', '/countries/greece'),
    #     ('Albania', ''),
    #     ('Republic of North Macedonia', '')],
    #    [('balkan_mediterranean.jpg')],
    # ],
    "Baltic Sea": [
        [
            ("Denmark", "/countries/denmark"),
            ("Estonia", "/countries/estonia"),
            ("Finland", "/countries/finland"),
            ("Germany", "/countries/germany"),
            ("Latvia", "/countries/latvia"),
            ("Lithuania", "/countries/lithuania"),
            ("Poland", "/countries/poland"),
            ("Sweden", "/countries/sweden"),
            ("Norway", "/countries/norway"),
        ],
        # ('Russia', ''),
        # ('Belarus', '')],
        [("baltic_sea.jpg")],
    ],
    "Black Sea Basin": [
        [
            ("Bulgaria", "/countries/bulgaria"),
            ("Georgia", ""),
            ("Greece", "/countries/greece"),
            ("the Republic of Moldova", ""),
            ("Romania", "/countries/romania"),
            ("Türkiye", "/countries/turkey"),
            ("Ukraine", ""),
        ],
        [("black_sea_basin.jpg")],
    ],
    "Central Europe": [
        [
            ("Austria", "/countries/austria"),
            ("Croatia", "/countries/croatia"),
            ("Czechia", "/countries/czech-republic"),
            ("Germany", "/countries/germany"),
            ("Hungary", "/countries/hungary"),
            ("Italy", "/countries/italy"),
            ("Poland", "/countries/poland"),
            ("Slovakia", "/countries/slovakia"),
            ("Slovenia", "/countries/slovenia"),
        ],
        [("central_europe.jpg")],
    ],
    "Danube": [
        [
            ("Austria", "/countries/austria"),
            ("Bulgaria", "/countries/bulgaria"),
            ("Croatia", "/countries/croatia"),
            ("Czechia", "/countries/czech-republic"),
            ("Germany", "/countries/germany"),
            ("Hungary", "/countries/hungary"),
            ("Romania", "/countries/romania"),
            ("Slovakia", "/countries/slovakia"),
            ("Slovenia", "/countries/slovenia"),
            ("Bosnia and Herzegovina", ""),
            ("Montenegro", ""),
            ("Serbia", ""),
            ("Ukraine", ""),
            ("Republic of Moldova", ""),
        ],
        [("danube.jpg")],
    ],
    "Mediterranean": [
        [
            ("Albania", ""),
            ("Bosnia and Herzegovina", ""),
            ("Bulgaria", "/countries/bulgaria"),
            ("Croatia", "/countries/croatia"),
            ("Cyprus", "/countries/cyprus"),
            ("France", "/countries/france"),
            ("Greece", "/countries/greece"),
            ("Italy", "/countries/italy"),
            ("Malta", "/countries/malta"),
            ("Montenegro", ""),
            ("Portugal", "/countries/portugal"),
            ("Republic of North Macedonia", ""),
            ("Slovenia", "/countries/slovenia"),
            ("Spain", "/countries/spain"),
        ],
        # ('United Kingdom', '/countries/united-kingdom')],
        [("mediterranean.jpg")],
    ],
    "Mediterranean Sea Basin": [
        [
            ("Algeria", ""),
            ("Cyprus", "/countries/cyprus"),
            ("Egypt", ""),
            ("France", "/countries/france"),
            ("Greece", "/countries/greece"),
            ("Israel", ""),
            ("Italy", "/countries/italy"),
            ("Lebanon", ""),
            ("Jordan", ""),
            ("Malta", "/countries/malta"),
            ("Palestine", ""),
            ("Portugal", "/countries/portugal"),
            ("Spain", "/countries/spain"),
            ("Tunisia", ""),
            ("Türkiye ", "/countries/turkey"),
        ],
        [("mediterranean_sea_basin.jpg")],
    ],
    "North Sea": [
        [
            ("Belgium", "/countries/belgium"),
            ("Denmark", "/countries/denmark"),
            ("Germany", "/countries/germany"),
            ("France", "/countries/france"),
            ("Netherlands", "/countries/netherlands"),
            ("Sweden", "/countries/sweden"),
            # ('United Kingdom', '/countries/united-kingdom'),
            ("Norway", "/countries/norway"),
        ],
        [("north_sea.jpg")],
    ],
    "North-West Europe": [
        [
            ("Belgium", "/countries/belgium"),
            ("France", "/countries/france"),
            ("Germany", "/countries/germany"),
            ("Ireland", "/countries/ireland"),
            ("Luxembourg", "/countries/luxembourg"),
            ("Netherlands", "/countries/netherlands"),
            ("Switzerland", "/countries/switzerland"),
        ],
        # ('United Kingdom', '/countries/united-kingdom')],
        [("north_western_europe.jpg")],
    ],
    "South-West Europe": [
        [
            ("France", "/countries/france"),
            ("Portugal", "/countries/portugal"),
            ("Spain", "/countries/spain"),
            # ('United Kingdom', '/countries/united-kingdom'),
            ("Andorra", ""),
        ],
        [("south_west_europe.jpg")],
    ],
    "Other regions": [[("", "")], [("")]],
}


def get_countries(context, data, current_lang):
    # a list of {'name': Country name, 'link': Country Link}
    region = data.get("region", None)

    if not region:
        return []

    current_regions = regions.get(region, None)
    if not current_regions:
        return []

    regions_translated = []

    for _r in current_regions[0]:
        path = _r[1]
        transl_path = path

        if path:
            transl_path = translated_url(context, path, current_lang)

        transl_path = transl_path.replace(
            "/countries/", "/countries-regions/countries/"
        )
        regions_translated.append((_r[0], transl_path))

    return [regions_translated, current_regions[1]]


def get_regions(current_lang):
    site = getSite()

    catalog = getToolByName(site, "portal_catalog")
    q = {
        "object_provides": ITransnationalRegionMarker.__identifier__,
        "sort_on": "getObjPositionInParent",
        "path": {"query": "/cca/{}".format(current_lang)},
    }
    brains = catalog.searchResults(**q)

    results = []

    for b in brains:
        # obj = b.getObject()
        # TODO: this needs to be translation-aware
        if b.Title.lower() in [
            "balkan-mediterranean area",
            "black sea basin",
            "mediterranean sea basin",
        ]:
            continue

        # if ITransnationalRegionMarker.providedBy(obj):
        results.append(b)

    return [{"url": b.getURL(), "title": b.Title} for b in results]


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class TransnationRegionSelectSerializationTransformer(object):
    order = 100
    block_type = "transRegionSelect"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if block.get("region"):
            current_lang = get_current_language(self.context, self.request)
            block["_v_"] = {
                "regions": get_regions(current_lang),
                "countries": get_countries(self.context, block, current_lang),
            }

        return block
