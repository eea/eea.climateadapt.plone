import json
import logging

import lxml.etree
import lxml.html

from Products.Five.browser import BrowserView

logger = logging.getLogger('eea.climateadapt')

_COUNTRIES_WITH_NAS = [
    "Austria", "Belgium", "Cyprus", "Czechia", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
    "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
    "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "United Kingdom",
    "Liechtenstein", "Norway", "Switzerland", "Turkey"
]

_COUNTRIES_WITH_NAP = [
    "Austria", "Belgium", "Cyprus", "Czechia", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Ireland", "Lithuania", "Netherlands",
    "Romania", "Spain", "United Kingdom", "Switzerland", "Turkey"
]

_MARKERS = [
    ('national adaption policy', 'National adaption policy'),
    ('national adaptation strategy', 'National adaptation strategy (NAS)'),
    ('national adaptation plan', 'National adaptation plan (NAP)'),

    # ('action plans', 'National adaptation plans (NAP)'),

    # ('action plans', 'Action plans'),
    # ('impacts', 'Impacts, vulnerability and adaptation assessments'),
    # ('climate services', 'Climate services / Met office'),

    # TODO: this is not found in the information extracted in DB
    # this needs to be fixed in content
    # ('adaptation platform', 'Adaptation platform'),
    #
    # ('web portal', 'Web portal'),
    # ('national communication', 'National Communication to the UNFCCC'),

    # ('monitoring', 'Monitoring, Indicators, Methodologies'),
    # ('research program', 'Research programs')
    # ('training', 'Training and education resources')
]


def normalized(key):
    """ Returns NAP/NAS label if they key is NAP or NAS
    """
    # We depend on human entered labels in the first column
    # We need to "normalize" it, because sometimes the case is wrong or some
    # parts of the text are missing (for example the NAS/NAP bit)

    for marker, label in _MARKERS:
        if marker in key.lower():
            return label


def get_nap_nas(obj, text, country):
    res = {}

    for name in ['nap', 'nas']:
        if obj.hasProperty(name):
            res[name] = obj.getProperty(name)

    # return res

    e = lxml.html.fromstring(text)
    rows = e.xpath('//table[contains(@class, "listing")]/tbody/tr')

    for row in rows:
        try:
            cells = row.xpath('td')
            # key = cells[0].text_content().strip()
            # key = ''.join(cells[0].itertext()).strip()
            key = ' '.join(
                [c for c in cells[0].itertext() if type(c) is not unicode])

            if key in [None, '']:
                key = cells[0].text_content().strip()

            if len(list(cells)) < 3:
                children = []
            else:
                children = list(cells[2])

            text = [lxml.etree.tostring(c) for c in children]
            value = u'\n'.join(text)
            key = normalized(key)

            if key is None:
                continue

            # If there's no text in the last column, write "Established".

            is_nap_country = country in _COUNTRIES_WITH_NAP
            is_nas_country = country in _COUNTRIES_WITH_NAS

            if (not value) and (is_nap_country or is_nas_country):
                value = u'<p>Established</p>'

            if "NAP" in key:
                prop = 'nap_info'
            else:
                prop = 'nas_info'

            # We're using a manually added property to set the availability of
            # NAP or NAS on a country. To use it, add two boolean properties:
            # nap and nas on the country folder. For example here:
            # /countries-regions/countries/ireland/manage_addProperty
            # is_nap_nas = obj.getProperty(prop, False)

            res[prop] = value

        except Exception:
            logger.exception(
                "Error in extracting information from country %s",
                country
            )

    return res


class CountriesMetadataExtract(BrowserView):
    """ Extract metadata from all country profiles, exports as json
    """

    def extract_country_metadata(self, obj):
        # if 'ireland' in obj.absolute_url().lower():
        #     import pdb
        #     pdb.set_trace()

        if 'index_html' in obj.contentIds():
            cover = obj['index_html']
        else:
            cover = obj

        layout = cover.cover_layout
        layout = json.loads(layout)

        try:
            main_tile = layout[0]['children'][1]['children'][1]
        except:
            main_tile = layout[0]['children'][0]['children'][2]

        assert main_tile['tile-type'] == 'collective.cover.richtext'

        uid = main_tile['id']
        tile_data = cover.__annotations__['plone.tiles.data.' + uid]
        text = tile_data['text'].raw

        res = get_nap_nas(obj, text, country=obj.Title())

        return res

    def __call__(self):
        res = {}

        for child in self.context.contentValues():
            if child.portal_type \
                    not in ['Folder', 'collective.cover.content']:
                continue

            res[child.Title()] = [
                self.extract_country_metadata(child),
                child.absolute_url()
            ]

        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps([res, [x[1] for x in _MARKERS]])


class CountryMetadataExtract(object):
    """ This is a demo view, shows metadata extracted from country

    It's not used in real code, it's mainly for debugging
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cover = self.context['index_html']

        layout = cover.cover_layout
        layout = json.loads(layout)

        try:
            main_tile = layout[0]['children'][1]['children'][1]
        except:
            main_tile = layout[0]['children'][0]['children'][2]

        assert main_tile['tile-type'] == 'collective.cover.richtext'

        uid = main_tile['id']
        tile_data = cover.__annotations__['plone.tiles.data.' + uid]
        text = tile_data['text'].raw

        e = lxml.etree.fromstring(text)
        rows = e.xpath('//table/tbody/tr')

        res = {}

        for row in rows:
            cells = row.xpath('td')
            # key = cells[0].text.strip()
            key = ''.join(cells[0].itertext()).strip()
            children = list(cells[2])
            text = [lxml.etree.tostring(c) for c in children]
            value = u'\n'.join(text)
            res[key] = value

        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps([res])


class CountriesD3View(BrowserView):
    """
    """


class ContextCountriesView(BrowserView):
    """ A small pagelet to show the countries as a tile
    """

    def countries(self):
        objects = self.context.aq_parent.contentValues()
        available_countries = [
            "Austria", "Belgium", "Cyprus", "Czechia", "Denmark", "Estonia",
            "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
            "Italy", "Lithuania", "Luxembourg", "Malta", "Netherlands",
            "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain",
            "Sweden", "United Kingdom", "Liechtenstein", "Norway",
            "Switzerland", "Turkey"
        ]
        return [x for x in objects if x.Title() in available_countries]

    def script_country_settings(self):
        context_titles = [x.Title()
                          for x in self.context.aq_parent.contentValues()]
        available_countries = [x for x in [
            "Austria", "Belgium", "Cyprus", "Czechia", "Denmark", "Estonia",
            "Finland", "France", "Germany", "Greece", "Hungary", "Ireland",
            "Italy", "Lithuania", "Luxembourg", "Malta", "Netherlands",
            "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain",
            "Sweden", "United Kingdom", "Liechtenstein", "Norway",
            "Switzerland", "Turkey"
        ] if x in context_titles]

        return """window.countrySettings = %s;""" % \
            json.dumps(available_countries)
