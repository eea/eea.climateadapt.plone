import json
import logging

import lxml.etree
import lxml.html

from Products.Five.browser import BrowserView

logger = logging.getLogger('eea.climateadapt')

_MARKERS = [
    ('national adaptation', 'National adaptation strategy'),
    ('action plans', 'Action plans'),
    ('impacts', 'Impacts, vulnerability and adaptation assessments'),
    ('climate services', 'Climate services / Met office'),

    # TODO: this is not found in the information extracted in DB
    # this needs to be fixed in content
    ('adaptation platform', 'Adaptation platform'),

    ('web portal', 'Web portal'),
    ('national communication', 'National Communication to the UNFCCC'),

    # ('monitoring', 'Monitoring, Indicators, Methodologies'),
    # ('research program', 'Research programs')
    # ('training', 'Training and education resources')
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
        main_tile = layout[0]['children'][1]['children'][1]
        assert main_tile['tile-type'] == 'collective.cover.richtext'

        uid = main_tile['id']
        tile_data = cover.__annotations__['plone.tiles.data.' + uid]
        text = tile_data['text'].raw

        e = lxml.html.fromstring(text)
        rows = e.xpath('//table[contains(@class, "listing")]/tbody/tr')

        res = {}
        if obj.getId() == 'latvia':
            import pdb
            pdb.set_trace()

        for row in rows:
            
            try:
                cells = row.xpath('td')
                key = cells[0].text_content().strip()
                children = list(cells[2])

                text = [lxml.etree.tostring(c) for c in children]
                value = u'\n'.join(text)
                key = normalized(key)

                if key is None:
                    continue
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
        main_tile = layout[0]['children'][1]['children'][1]
        assert main_tile['tile-type'] == 'collective.cover.richtext'

        uid = main_tile['id']
        tile_data = cover.__annotations__['plone.tiles.data.' + uid]
        text = tile_data['text'].raw

        e = lxml.etree.fromstring(text)
        rows = e.xpath('//table/tbody/tr')

        res = {}

        for row in rows:
            cells = row.xpath('td')
            key = cells[0].text.strip()
            children = list(cells[2])
            text = [lxml.etree.tostring(c) for c in children]
            value = u'\n'.join(text)
            res[key] = value

        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps([res])


# class CountriesD3View(BrowserView):
#     """
#     """

    # def text(self):
    #     import pdb
    #     pdb.set_trace()
    #     page = self.context

    #     text = "bla"

    #     return text
