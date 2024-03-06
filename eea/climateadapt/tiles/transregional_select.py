# -*- coding: utf-8 -*-
""" A tile to implement the transregional select dropdown
"""

from collective.cover.tiles.base import (IPersistentCoverTile,
                                         PersistentCoverTile)
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements, providedBy

from eea.climateadapt.translation.utils import TranslationUtilsMixin


class ITransRegionalSelectTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=u'Title',
        required=False,
    )

    region = schema.Choice(
        title=u"Region",
        vocabulary="eea.climateadapt.regions",
        required=True,
    )


regions = {
    'Adriatic-Ionian': [
        [('Croatia', '/countries/croatia'),
         ('Greece', '/countries/greece'),
         ('Italy', '/countries/italy'),
         ('Slovenia', '/countries/slovenia'),
         ('Albania', ''),
         ('Bosnia and Herzegovina', ''),
         ('Montenegro', ''),
         ('Republic of North Macedonia', ''),
         ('Serbia', '')],
        [('adriatic _ionian.jpg')],
    ],
    'Alpine Space': [
        [('Austria', '/countries/austria'),
         ('France', '/countries/france'),
         ('Germany', '/countries/germany'),
         ('Italy', '/countries/italy'),
         ('Slovenia', '/countries/slovenia'),
         ('Liechtenstein', ''),
         ('Switzerland', '/countries/switzerland')],
        [('alpine_space.jpg')],
    ],
    'Northern Periphery and Artic': [
        [('Finland', '/countries/finland'),
         ('Ireland', '/countries/ireland'),
         ('Sweden', '/countries/sweden'),
         # ('United Kingdom', '/countries/united-kingdom'),
         ('Iceland', '/countries/iceland'),
         ('Norway', '/countries/norway'),
         ('Greenland', ''),
         ('Faroe Islands', '')],
        [('northern_periphery_and_arctic.jpg')],
    ],
    'Atlantic': [
        [('France', '/countries/france'),
         ('Ireland', '/countries/ireland'),
         ('Portugal', '/countries/portugal'),
         ('Spain', '/countries/spain')
         # ('United Kingdom', '/countries/united-kingdom')
         ],
        [('atlantic_area.jpg')],
    ],
    # 'Balkan-Mediterranean': [
    #    [('Bulgaria', '/countries/bulgaria'),
    #     ('Cyprus', '/countries/cyprus'),
    #     ('Greece', '/countries/greece'),
    #     ('Albania', ''),
    #     ('Republic of North Macedonia', '')],
    #    [('balkan_mediterranean.jpg')],
    # ],
    'Baltic Sea': [
        [('Denmark', '/countries/denmark'),
         ('Estonia', '/countries/estonia'),
         ('Finland', '/countries/finland'),
         ('Germany', '/countries/germany'),
         ('Latvia', '/countries/latvia'),
         ('Lithuania', '/countries/lithuania'),
         ('Poland', '/countries/poland'),
         ('Sweden', '/countries/sweden'),
         ('Norway', '/countries/norway')],
        # ('Russia', ''),
        # ('Belarus', '')],
        [('baltic_sea.jpg')],
    ],
    'Black Sea Basin': [
        [('Bulgaria', '/countries/bulgaria'),
         ('Georgia', ''),
         ('Greece', '/countries/greece'),
         ('the Republic of Moldova', ''),
         ('Romania', '/countries/romania'),
         ('Türkiye', '/countries/turkey'),
         ('Ukraine', '')],
        [('black_sea_basin.jpg')],
    ],
    'Central Europe': [
        [('Austria', '/countries/austria'),
         ('Croatia', '/countries/croatia'),
         ('Czechia', '/countries/czech-republic'),
         ('Germany', '/countries/germany'),
         ('Hungary', '/countries/hungary'),
         ('Italy', '/countries/italy'),
         ('Poland', '/countries/poland'),
         ('Slovakia', '/countries/slovakia'),
         ('Slovenia', '/countries/slovenia')],
        [('central_europe.jpg')],
    ],
    'Danube': [
        [('Austria', '/countries/austria'),
         ('Bulgaria', '/countries/bulgaria'),
         ('Croatia', '/countries/croatia'),
         ('Czechia', '/countries/czech-republic'),
         ('Germany', '/countries/germany'),
         ('Hungary', '/countries/hungary'),
         ('Romania', '/countries/romania'),
         ('Slovakia', '/countries/slovakia'),
         ('Slovenia', '/countries/slovenia'),
         ('Bosnia and Herzegovina, ', ''),
         ('Montenegro', ''),
         ('Serbia', ''),
         ('Ukraine', ''),
         ('Republic of Moldova', '')],
        [('danube.jpg')],
    ],
    'Mediterranean': [
        [('Albania', ''),
         ('Bosnia and Herzegovina', ''),
         ('Bulgaria', '/countries/bulgaria'),
         ('Croatia', '/countries/croatia'),
         ('Cyprus', '/countries/cyprus'),
         ('France', '/countries/france'),
         ('Greece', '/countries/greece'),
         ('Italy', '/countries/italy'),
         ('Malta', '/countries/malta'),
         ('Montenegro', ''),
         ('Portugal', '/countries/portugal'),
         ('Republic of North Macedonia', ''),
         ('Slovenia', '/countries/slovenia'),
         ('Spain', '/countries/spain')],
        # ('United Kingdom', '/countries/united-kingdom')],
        [('mediterranean.jpg')],
    ],
    'Mediterranean Sea Basin': [
        [('Algeria', ''),
         ('Cyprus', '/countries/cyprus'),
         ('Egypt', ''),
         ('France', '/countries/france'),
         ('Greece', '/countries/greece'),
         ('Israel', ''),
         ('Italy', '/countries/italy'),
         ('Lebanon', ''),
         ('Jordan', ''),
         ('Malta', '/countries/malta'),
         ('Palestine', ''),
         ('Portugal', '/countries/portugal'),
         ('Spain', '/countries/spain'),
         ('Tunisia', ''),
         ('Türkiye ', '/countries/turkey')],
        [('mediterranean_sea_basin.jpg')],
    ],
    'North Sea': [
        [('Belgium', '/countries/belgium'),
         ('Denmark', '/countries/denmark'),
         ('Germany', '/countries/germany'),
         ('France', '/countries/france'),
         ('Netherlands', '/countries/netherlands'),
         ('Sweden', '/countries/sweden'),
         # ('United Kingdom', '/countries/united-kingdom'),
         ('Norway', '/countries/norway')],
        [('north_sea.jpg')],
    ],
    'North-West Europe': [
        [('Belgium', '/countries/belgium'),
         ('France', '/countries/france'),
         ('Germany', '/countries/germany'),
         ('Ireland', '/countries/ireland'),
         ('Luxembourg', '/countries/luxembourg'),
         ('Netherlands', '/countries/netherlands'),
         ('Switzerland', '/countries/switzerland')],
        # ('United Kingdom', '/countries/united-kingdom')],
        [('north_western_europe.jpg')],
    ],
    'South-West Europe': [
        [('France', '/countries/france'),
         ('Portugal', '/countries/portugal'),
         ('Spain', '/countries/spain'),
         # ('United Kingdom', '/countries/united-kingdom'),
         ('Andorra', '')],
        [('south_west_europe.jpg')],
    ],
    'Other regions': [
        [('', '')],
        [('')]
    ],
}


class TransRegionalSelectTile(PersistentCoverTile, TranslationUtilsMixin):
    """ TransRegionalSelect tile

    Shows a dropdown select for a region
    """

    implements(ITransRegionalSelectTile)

    index = ViewPageTemplateFile('pt/transregional_select.pt')

    is_configurable = False
    is_editable = True
    is_droppable = False
    short_name = u'Select trans region'

    def is_empty(self):
        return False

    def regions(self):
        site = getSite()

        catalog = getToolByName(site, 'portal_catalog')
        q = {
            "object_provides":
                "eea.climateadapt.interfaces.ITransnationalRegionMarker",
            'sort_on': 'getObjPositionInParent',
            "path": {"query": "/cca/{}".format(self.current_lang)}
        }
        brains = catalog.searchResults(**q)

        results = []

        for b in brains:
            obj = b.getObject()
            if obj.title.lower() in [
                'balkan-mediterranean area',
                'black sea basin',
                'mediterranean sea basin'
            ]:
                continue
            provides = ["%s.%s" % (iface.__module__ or '', iface.__name__)
                        for iface in providedBy(obj)]

            if "eea.climateadapt.interfaces.ITransnationalRegionMarker" \
                    in provides:
                results.append(b)

        return [{'url': b.getURL(), 'title': b.Title} for b in results]

    def countries(self):
        # a list of {'name': Country name, 'link': Country Link}
        region = self.data.get('region', None)

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
                transl_path = self.translated_url(path)

            transl_path = transl_path.replace(
                '/countries/', '/countries-regions/countries/')
            regions_translated.append((_r[0], transl_path))

        return [regions_translated, current_regions[1]]
