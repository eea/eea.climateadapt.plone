import json
import logging

import lxml.etree
import lxml.html

from Products.Five.browser import BrowserView

logger = logging.getLogger('eea.climateadapt')

_MARKERS = [
    ('national adaptation', 'National adaptation strategy (NAS)'),
    ('action plans', 'National adaptation plans (NAP)'),
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


_COUNTRIES_WITH_NAS = [
    "Austria", "Belgium", "Cyprus", "Czech Republic", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Greece", "Hungary", "Ireland", "Italy",
    "Lithuania", "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
    "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "United Kingdom",
    "Liechtenstein", "Norway", "Switzerland", "Turkey"
]

_COUNTRIES_WITH_NAP = [
    "Austria", "Belgium", "Cyprus", "Czech Republic", "Denmark", "Estonia",
    "Finland", "France", "Germany", "Ireland", "Lithuania", "Netherlands",
    "Romania", "Spain", "United Kingdom", "Switzerland", "Turkey"
]


def normalized(key):

    for marker, label in _MARKERS:
        if marker in key.lower():
            return label


class CountriesMetadataExtract(BrowserView):
    """ Extract metadata from all country profiles, exports as json
    """

    def extract_country_metadata(self, obj):
        cover = obj['index_html']

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

        e = lxml.html.fromstring(text)
        rows = e.xpath('//table[contains(@class, "listing")]/tbody/tr')

        res = {}

        for row in rows:

            try:
                cells = row.xpath('td')
                # key = cells[0].text_content().strip()
                # key = ''.join(cells[0].itertext()).strip()
                key = ' '.join(
                    [c for c in cells[0].itertext() if type(c) is not unicode])
                children = list(cells[2])

                if key in [None, '']:
                    key = cells[0].text_content().strip()

                text = [lxml.etree.tostring(c) for c in children]
                value = u'\n'.join(text)
                key = normalized(key)

                if key is None:
                    continue

                if 'NAP' in key:
                    if obj.Title() in _COUNTRIES_WITH_NAP:
                        if len(text) == 0:
                            text.append('<p>Established</p>')
                            value = u'\n'.join(text)
                    else:
                        value = u''
                else:
                    if obj.Title() in _COUNTRIES_WITH_NAS:
                        if len(text) == 0:
                            text.append('<p>Established</p>')
                            value = u'\n'.join(text)
                    else:
                        value = u''
                res[key] = value
            except Exception:
                logger.warning(
                    "Error in extracting information from country %s",
                    obj.Title()
                )

        return res

    def __call__(self):
        res = {}

        for child in self.context.contentValues():
            if child.portal_type != 'Folder':
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
