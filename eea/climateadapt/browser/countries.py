import csv
import json
import logging
import re
import sys
from datetime import datetime

import lxml.etree
import lxml.html
import urllib2
from eea.climateadapt.vocabulary import ace_countries
from pkg_resources import resource_filename
from plone.api import portal
from plone.intelligenttext.transforms import (
    WebIntelligentToHtmlConverter,
    convertWebIntelligentPlainTextToHtml as convWebInt,
    safe_decode
)
from eea.climateadapt.translation.utils import (
    TranslationUtilsMixin,
    translate_text,
    get_current_language
)
from eea.climateadapt import MessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


def parse_csv(path):
    wf = resource_filename("eea.climateadapt", path)

    reader = csv.reader(open(wf))
    cols = reader.next()
    out = []

    for line in reader:
        out.append(dict(zip(cols, line)))

    return out


def get_country_code(country_name):
    country_code = next(
        (k for k, v in ace_countries if v == country_name), 'Not found'
    )

    return country_code


def setup_discodata(annotations):
    response = urllib2.urlopen(DISCODATA_URL)
    data = json.loads(response.read())
    annotations['discodata'] = {
        'timestamp': datetime.now(),
        'data': data
    }
    annotations._p_changed = True
    logger.info("RELOAD URL %s", DISCODATA_URL)

    return data


def get_discodata():
    annotations = portal.getSite().__annotations__

    if 'discodata' not in annotations:
        annotations._p_changed = True
        return setup_discodata(annotations)

    last_import_date = annotations['discodata']['timestamp']

    if (datetime.now() - last_import_date).total_seconds() > 60 * 2:
        annotations._p_changed = True
        return setup_discodata(annotations)

    return annotations['discodata']['data']


def get_discodata_for_country(country_code):
    data = get_discodata()

    orig_data = next((
        x
        for x in data['results']
        if x['countryCode'] == country_code
    ), {})

    # remove the countryCode as we don't need it
    processed_data = {
        k: unicode(v)
        for k, v in orig_data.items()
        # if k != 'countryCode'
        if k not in ['countryCode', 'ReportNet3HistoricReleaseId']
    }

    # some values are strings, and need to be transformed
    # into Python objects
    for k, val in processed_data.items():
        # import pdb; pdb.set_trace()
        json_val = json.loads(val)
        new_value = json_val[k][0]

        processed_data[k] = new_value

    return processed_data


# DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_JSON%5D&p=1&nrOfHits=100'
DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2023%5D&p=1&nrOfHits=100'


logger = logging.getLogger("eea.climateadapt")

_COUNTRIES_WITH_NAS = [
    "Austria",
    "Belgium",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "United Kingdom",
    "Liechtenstein",
    "Norway",
    "Switzerland",
    "Turkey",
]

_COUNTRIES_WITH_NAP = [
    "Austria",
    "Belgium",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Ireland",
    "Lithuania",
    "Netherlands",
    "Romania",
    "Spain",
    "United Kingdom",
    "Switzerland",
    "Turkey",
]

_MARKERS = [
    ("national adaption policy", _("National adaption policy")),
    ("climate change impact and vulnerability assessments",
     _("Climate change impact and vulnerability assessments")),
    ("adaptation portals and platforms", _("Adaptation portals and platforms")),
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
    """Returns NAP/NAS label if they key is NAP or NAS"""
    # We depend on human entered labels in the first column
    # We need to "normalize" it, because sometimes the case is wrong or some
    # parts of the text are missing (for example the NAS/NAP bit)

    for marker, label in _MARKERS:
        if marker in key.lower():
            return label


def get_nap_nas(obj, text, country):
    res = {}

    for name in ["nap", "nas"]:
        if obj.hasProperty(name):
            res[name] = obj.getProperty(name)

    # return res

    e = lxml.html.fromstring(text)
    rows = e.xpath('//table[contains(@class, "listing")]/tbody/tr')

    for row in rows:
        try:
            cells = row.xpath("td")
            # key = cells[0].text_content().strip()
            # key = ''.join(cells[0].itertext()).strip()
            key = " ".join([c for c in cells[0].itertext() if type(c) is not unicode])

            if key in [None, ""]:
                key = cells[0].text_content().strip()

            if len(list(cells)) < 3:
                children = []
            else:
                children = list(cells[2])

            text = [lxml.etree.tostring(c) for c in children]
            value = u"\n".join(text)
            key = normalized(key)

            if key is None:
                continue

            # If there's no text in the last column, write "Established".

            is_nap_country = country in _COUNTRIES_WITH_NAP
            is_nas_country = country in _COUNTRIES_WITH_NAS

            if (not value) and (is_nap_country or is_nas_country):
                value = u"<p>Established</p>"

            if "NAP" in key:
                prop = "nap_info"
            else:
                prop = "nas_info"

            # We're using a manually added property to set the availability of
            # NAP or NAS on a country. To use it, add two boolean properties:
            # nap and nas on the country folder. For example here:
            # /countries-regions/countries/ireland/manage_addProperty
            # is_nap_nas = obj.getProperty(prop, False)

            res[prop] = value

        except Exception:
            logger.exception("Error in extracting information from country %s", country)

    return res


PY3 = sys.version_info[0] == 3
if PY3:
    from html.entities import name2codepoint
    unicode = str
    unichr = chr
else:
    from htmlentitydefs import name2codepoint


class CCAWebIntelligentToHtmlConverter(WebIntelligentToHtmlConverter):
    newline_regex = re.compile('\\n+(?=[A-Z])')  #(?=\\p{L})
    tabnewline_regex = re.compile('(\\r\\n)+')

    def __call__(self):
        text = self.orig
        if text is None:
            text = ''

        text = safe_decode(text, errors='replace')

        # Do &amp; separately, else, it may replace an already-inserted & from
        # an entity with &amp;, so < becomes &lt; becomes &amp;lt;
        text = text.replace('&', '&amp;')
        # Make funny characters into html entity defs
        for entity, codepoint in name2codepoint.items():
            if entity != 'amp':
                text = text.replace(unichr(codepoint), '&' + entity + ';')

        text = self.urlRegexp.subn(self.replaceURL, text)[0]
        text = self.emailRegexp.subn(self.replaceEmail, text)[0]
        text = self.indentRegexp.subn(self.indentWhitespace, text)[0]

        # convert windows line endings
        # text = text.replace('\r\n', '\n')
        text = self.tabnewline_regex.sub('\n', text)
        text = self.newline_regex.sub('\n\n', text)
        # Finally, make \n's into br's
        text = text.replace('\n', '<br />')

        if not PY3:
            text = text.encode('utf-8')

        return text


class CountriesMetadataExtract(BrowserView, TranslationUtilsMixin):
    """Extract metadata from all country profiles, exports as json"""

    def extract_country_metadata_discodata(self, obj):
        res = {}

        # for name in ["nap", "nas", "sap"]:
        #     if obj.hasProperty(name):
        #         res[name] = obj.getProperty(name)

        country_name = obj.id.title().replace('-', ' ')
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)

        if not processed_data:
            res['notreported'] = True

            return res

        # setup National adaptation policy - NAS, NAP and SAP
        for name in ('NAS', 'NAP', 'SAP'):
            value = u''
            values = processed_data['Legal_Policies'].get(name, [])
            is_nap_country = country_name in _COUNTRIES_WITH_NAP
            is_nas_country = country_name in _COUNTRIES_WITH_NAS

            # if (not values) and (is_nap_country or is_nas_country):
            #     value = u"<p>Established</p>"

            if values:
                if name == 'SAP':
                    value = [
                        u"<li><a href='{0}'>{1}</a><p {5}>{3}</p>"
                        u"<p {4}>{2}</p></li>".format(
                            v.get('Link'), v.get('Title'),
                            v.get('Status'), v.get('Sector'),
                            "style='font-style:oblique;'",
                            "style='font-weight:bold;'",
                        )
                        for v in values
                    ]
                else:
                    value = [
                        u"<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                            v.get('Link'), v.get('Title'),
                            "style='font-style:oblique;'", v.get('Status'))
                        for v in values
                    ]
                value = u"<ul>{}</ul>".format(
                    ''.join(value)
                )

            prop = "{}_info".format(name.lower())

            res[prop] = value

        # setup Climate change impact and vulnerability assessments
        value = u""
        values = processed_data['National_Circumstances'].get('CC_IVA', [])
        if values:
            value = [
                u"<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                    v.get('Link'), v.get('Title'),
                    "style='font-style:oblique;'", v.get('Status'))
                for v in values
            ]
            value = u"<ul>{}</ul>".format(
                ''.join(value)
            )

        res["cciva_info"] = value

        # setup Adaptation portals and platforms
        value = u""
        values = processed_data['Contact'].get('CCIV_Portal_Platform', [])
        if values:
            value = [
                u"<li><a href='{0}'>{1}</a><p {5}>{3}</p>"
                u"<p {4}>{2}</p></li>".format(
                    v.get('Website'), v.get('Name'),
                    v.get('Status'), v.get('Focus'),
                    "style='font-style:oblique;'",
                    "style='font-weight:bold;'",
                )
                for v in values
            ]
            value = u"<ul>{}</ul>".format(
                ''.join(value)
            )

            focus_vals = [
                f
                for focus in values
                for f in focus.get('Focus', '').split('; ')
            ]
            hazard = "Climate change hazards, impact and/or vulnerability"
            adapt = "Climate change adaptation (measures and solutions)"

            if hazard in focus_vals and adapt in focus_vals:
                focus_info = "both"
            elif hazard in focus_vals and adapt not in focus_vals:
                focus_info = "hazard"
            elif hazard not in focus_vals and adapt in focus_vals:
                focus_info = "adaptation"
            else:
                focus_info = "not_specified"

            res["focus_info"] = focus_info

        res["ccivportal_info"] = value

        return res

    def extract_country_metadata(self, obj):
        # if 'ireland' in obj.absolute_url().lower():
        #     import pdb
        #     pdb.set_trace()

        if "index_html" in obj.contentIds():
            cover = obj["index_html"]
        else:
            cover = obj

        layout = cover.cover_layout
        layout = json.loads(layout)

        try:
            main_tile = layout[0]["children"][1]["children"][1]
        except:
            main_tile = layout[0]["children"][0]["children"][2]

        assert main_tile["tile-type"] == "collective.cover.richtext"

        uid = main_tile["id"]
        tile_data = cover.__annotations__["plone.tiles.data." + uid]
        text = tile_data["text"].raw

        res = get_nap_nas(obj, text, country=obj.id.title().replace('-', ' '))
        res['notreported'] = True

        return res

    def __call__(self):
        res = {}

        for child in self.context.contentValues():
            if child.portal_type not in ["Folder", "collective.cover.content"]:
                continue

            try:
                c_metadata = self.extract_country_metadata(child)
            except:
                c_metadata = self.extract_country_metadata_discodata(child)

            if not c_metadata:
                c_metadata = self.extract_country_metadata_discodata(child)
            
            res[child.id.title().replace('-', ' ')] = [
                c_metadata,
                child.absolute_url(),
            ]

        self.request.response.setHeader("Content-type", "application/json")
        data = [];
        for marker in _MARKERS:
            data.append([marker[1],translate_text(self.context, self.request, marker[1], 'eea.cca', self.current_lang)])

        return json.dumps([res, [x[1] for x in _MARKERS], data])


class CountryMetadataExtract(object):
    """This is a demo view, shows metadata extracted from country

    It's not used in real code, it's mainly for debugging
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cover = self.context["index_html"]

        layout = cover.cover_layout
        layout = json.loads(layout)

        try:
            main_tile = layout[0]["children"][1]["children"][1]
        except:
            main_tile = layout[0]["children"][0]["children"][2]

        assert main_tile["tile-type"] == "collective.cover.richtext"

        uid = main_tile["id"]
        tile_data = cover.__annotations__["plone.tiles.data." + uid]
        text = tile_data["text"].raw

        e = lxml.etree.fromstring(text)
        rows = e.xpath("//table/tbody/tr")

        res = {}

        for row in rows:
            cells = row.xpath("td")
            # key = cells[0].text.strip()
            key = "".join(cells[0].itertext()).strip()
            children = list(cells[2])
            text = [lxml.etree.tostring(c) for c in children]
            value = u"\n".join(text)
            res[key] = value

        self.request.response.setHeader("Content-type", "application/json")

        return json.dumps([res])


class CountriesD3View(BrowserView):
    """"""


class ContextCountriesView(BrowserView):
    """A small pagelet to show the countries as a tile"""

    available_countries = [
        "Austria",
        "Belgium",
        "Bulgaria",
        "Croatia",
        "Iceland",
        "Latvia",
        "Cyprus",
        "Czechia",
        "Denmark",
        "Estonia",
        "Finland",
        "France",
        "Germany",
        "Greece",
        "Hungary",
        "Ireland",
        "Italy",
        "Lithuania",
        "Luxembourg",
        "Malta",
        "Netherlands",
        "Poland",
        "Portugal",
        "Romania",
        "Slovakia",
        "Slovenia",
        "Spain",
        "Sweden",
        "United Kingdom",
        "Liechtenstein",
        "Norway",
        "Switzerland",
        "Turkey",
    ]

    def countries(self):
        objects = self.context.aq_parent.contentValues()

        return sorted(
            [
                x for x in objects
                if x.id.title().replace('-', ' ') in self.available_countries
            ],key=lambda x: x.id.title().replace('-', ' '),
        )

    def script_country_settings(self):
        context_titles = [
            x.id.title().replace('-', ' ')
            for x in self.context.aq_parent.contentValues()
        ]
        available_countries = [
            x for x in self.available_countries if x in context_titles
        ]

        return """window.countrySettings = %s;""" % json.dumps(available_countries)

    def csv_data_js(self):
        # used for heat_index map
        info = parse_csv("data/heat_index.csv")
        m = {}

        for line in info:
            if line["country_id"].strip():
                m[line["country_id"]] = line

        s = """var heat_index_info = {0};console.log(heat_index_info);""".format(
            json.dumps(m)
        )

        return s


class CountryProfileData(BrowserView):
    template = ViewPageTemplateFile("pt/country-profile.pt")

    def convert_web_int(self, text):
        _text = CCAWebIntelligentToHtmlConverter(text.strip())()

        # import pdb; pdb.set_trace()

        return _text
        # return convWebInt(text.strip())

    def get_sorted_affected_sectors_data(self):
        items = self.processed_data['National_Circumstances'].get(
            'Afected_Sectors', [])

        sorted_items = sorted(
            items,
            key=lambda i: (i['SectorTitle'], i['SectorDescribeIfOther'] if 'SectorDescribeIfOther' in i else '')
        )

        return sorted_items

    def get_sorted_action_measures_data(self):
        items = self.processed_data['Strategies_Plans'].get(
            'Action_Measures', [])

        sorted_items = sorted(
            items,
            key=lambda i: (i['KeyTypeMeasure'], i['subKTM'], i['Title'])
        )

        return sorted_items

    def get_sorted_available_practices_data(self):
        items = self.processed_data['Cooperation_Experience'].get(
            'AvailableGoodPractices', [])

        sorted_items = sorted(
            items,
            key=lambda i: i['Title']
        )

        return sorted_items

    def fix_link(self, link):
        """ Fix links like www.website.com
        """
        if link != "#" and 'http' not in link:
            return "http://" + link

        return link

    def summary_table(self):
        country_name = self.context.id.title().replace('-', ' ')
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        response = {}
        items = processed_data.get('Legal_Policies',[]).get('AdaptationPolicies',[])
        for item in items:
            typeName = item['Type']
            temp = typeName.split(':',1)
            if len(temp)==2:
                typeName = temp[1]
            if typeName not in response.keys():
                response[typeName] = []
            response[typeName].append({'status':item['Status'], 'title':item['Title'],'link':self.fix_link(item.get('Link','#'))})

        #import pdb; pdb.set_trace()

        keys = response.keys()
        keys.sort()
        return {'keys':keys, 'items':response}

    def __call__(self):
        country_name = self.context.id.title().replace('-', ' ')
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        self.processed_data = processed_data
        #import pdb; pdb.set_trace()
        return self.template(country_data=processed_data)


class CountryProfileDataRaw(CountryProfileData):
    template = ViewPageTemplateFile("pt/country-profile-raw.pt")
