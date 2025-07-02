import csv
import json
import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import OrderedDict
from datetime import datetime
from html.entities import name2codepoint

import lxml.etree
import lxml.html
from pkg_resources import resource_filename
from plone.api import portal
from plone.intelligenttext.transforms import WebIntelligentToHtmlConverter, safe_decode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.translation.utils import TranslationUtilsMixin, translate_text
from eea.climateadapt.vocabulary import ace_countries


def parse_csv(path):
    wf = resource_filename("eea.climateadapt", path)

    reader = csv.reader(open(wf))
    cols = next(reader)
    out = []

    for line in reader:
        out.append(dict(list(zip(cols, line))))

    return out


def get_country_code(country_name):
    if 'Moldova' == country_name:
        country_name = 'Moldova, Republic of'
    if 'Moldavia' == country_name:
        country_name = 'Moldova, Republic of'
    country_code = next(
        (k for k, v in ace_countries if v == country_name), "Not found")
    if country_code == "GR":
        country_code = "EL"
    if country_code == "Not found" and country_name.lower() == "turkiye":
        country_code = "TR"

    return country_code


def setup_discodata(annotations, is_energy_comunity=False):
    call_discodata_url = DISCODATA_ENERGY_COMUNITY_URL if is_energy_comunity else DISCODATA_URL
    response = urllib.request.urlopen(call_discodata_url)
    data = json.loads(response.read())
    annotations_discodata_key = "discodata_country_2025"
    if is_energy_comunity:
        annotations_discodata_key += "_energy_comunity"
    annotations[annotations_discodata_key] = {
        "timestamp": datetime.now(), "data": data}
    annotations._p_changed = True
    logger.info("RELOAD URL %s", call_discodata_url)

    return data


def get_discodata(is_energy_comunity=False):
    annotations = portal.getSite().__annotations__

    # import pdb
    # pdb.set_trace()

    annotations_discodata_key = "discodata_country_2025"
    if is_energy_comunity:
        annotations_discodata_key += "_energy_comunity"

    if annotations_discodata_key not in annotations:
        annotations._p_changed = True
        return setup_discodata(annotations, is_energy_comunity)

    last_import_date = annotations[annotations_discodata_key]["timestamp"]

    if (datetime.now() - last_import_date).total_seconds() > 60**2:
        # if (datetime.now() - last_import_date).total_seconds() > 0:
        # if (datetime.now() - last_import_date).total_seconds() > 60:
        annotations._p_changed = True
        return setup_discodata(annotations, is_energy_comunity)

    return annotations[annotations_discodata_key]["data"]


def get_discodata_for_country(country_code):
    data = get_discodata(country_code.upper() in ['GE', 'MD', 'RS', 'UA'])
    # import pdb; pdb.set_trace()

    orig_data = next(
        (x for x in data["results"] if x["countryCode"] == country_code), {}
    )

    # import pdb; pdb.set_trace()
    # remove the countryCode as we don't need it
    processed_data = {
        k: str(v)
        for k, v in list(orig_data.items())
        if k not in ["countryCode", "ReportNet3HistoricReleaseId"]
    }

    # some values are strings, and need to be transformed
    # import pdb; pdb.set_trace()
    # into Python objects
    for k, val in list(processed_data.items()):
        try:
            if val == "None":
                processed_data[k] = None
                continue
            json_val = json.loads(val)
            new_value = None

            if isinstance(json_val, dict):
                new_value = json_val[k][0] if 1 == len(
                    json_val[k]) else json_val[k]

                processed_data[k] = new_value
            # else:
            #    processed_data[k] = None
        except:
            logger.info("EMPTY DATA 114 : %s", k)

    return processed_data


# DISCODATA_URL = 'https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_JSON%5D&p=1&nrOfHits=100'
# DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2023%5D&p=1&nrOfHits=100"
DISCODATA_URL = "https://discodata.eea.europa.eu/sql?query=Select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BAdaptation_Art19_JSON_2025%5D&p=1&nrOfHits=50&mail=null&schema=null"
DISCODATA_ENERGY_COMUNITY_URL = "https://discodata.eea.europa.eu/sql?query=Select%20*%20from%20%5BNCCAPS%5D.%5Blatest%5D.%5BEC_Adaptation_Art19_JSON_2025%5D&p=1&nrOfHits=50&mail=null&schema=null"
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
    # "United Kingdom",
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
    # "United Kingdom",
    "Switzerland",
    "Turkey",
]

_MARKERS = [
    ("national adaption policy", _("National adaption policy")),
    # ("climate change impact and vulnerability assessments",
    #  _("Climate change impact and vulnerability assessments")),
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
            key = " ".join(
                [c for c in cells[0].itertext() if type(c) is not str])

            if key in [None, ""]:
                key = cells[0].text_content().strip()

            if len(list(cells)) < 3:
                children = []
            else:
                children = list(cells[2])

            text = [lxml.etree.tostring(c) for c in children]
            value = "\n".join(text)
            key = normalized(key)

            if key is None:
                continue

            # If there's no text in the last column, write "Established".

            is_nap_country = country in _COUNTRIES_WITH_NAP
            is_nas_country = country in _COUNTRIES_WITH_NAS

            if (not value) and (is_nap_country or is_nas_country):
                value = "<p>Established</p>"

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
            logger.exception(
                "Error in extracting information from country %s", country)

    return res


PY3 = sys.version_info[0] == 3


class CCAWebIntelligentToHtmlConverter(WebIntelligentToHtmlConverter):
    newline_regex = re.compile("\\n+(?=[A-Z])")  # (?=\\p{L})
    tabnewline_regex = re.compile("(\\r\\n)+")

    def __call__(self):
        text = self.orig
        if text is None:
            text = ""

        text = safe_decode(text, errors="replace")

        # Do &amp; separately, else, it may replace an already-inserted & from
        # an entity with &amp;, so < becomes &lt; becomes &amp;lt;
        text = text.replace("&", "&amp;")
        # Make funny characters into html entity defs
        for entity, codepoint in list(name2codepoint.items()):
            if entity != "amp":
                text = text.replace(chr(codepoint), "&" + entity + ";")

        text = self.urlRegexp.subn(self.replaceURL, text)[0]
        text = self.emailRegexp.subn(self.replaceEmail, text)[0]
        text = self.indentRegexp.subn(self.indentWhitespace, text)[0]

        # convert windows line endings
        # text = text.replace('\r\n', '\n')
        text = self.tabnewline_regex.sub("\n", text)
        text = self.newline_regex.sub("\n\n", text)
        # Finally, make \n's into br's
        text = text.replace("\n", "<br />")

        if not PY3:
            text = text.encode("utf-8")

        return text


class CountriesMetadataExtract(TranslationUtilsMixin):
    """Extract metadata from all country profiles, exports as json"""

    def extract_country_metadata_discodata(self, obj):
        res = {}

        # for name in ["nap", "nas", "sap"]:
        #     if obj.hasProperty(name):
        #         res[name] = obj.getProperty(name)

        country_name = obj.id.title().replace("-", " ")
        if country_name.lower == "turkiye":
            country_name == "Turkey"
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)

        if not processed_data:
            res["notreported"] = True

            return res

        if not processed_data["Legal_Policies"]:
            return res

        # setup National adaptation policy - NAS, NAP and SAP
        for name in ("NAS", "NAP", "SAP"):
            value = ""
            values = processed_data["Legal_Policies"].get(name, [])

            # is_nap_country = country_name in _COUNTRIES_WITH_NAP
            # is_nas_country = country_name in _COUNTRIES_WITH_NAS

            # if (not values) and (is_nap_country or is_nas_country):
            #     value = u"<p>Established</p>"

            if values:
                if name == "SAP":
                    value = [
                        "<li><a href='{0}'>{1}</a><p {5}>{3}</p>"
                        "<p {4}>{2}</p></li>".format(
                            v.get("Link"),
                            v.get("Title"),
                            v.get("Status"),
                            v.get("Sector"),
                            "style='font-style:oblique;'",
                            "style='font-weight:bold;'",
                        )
                        for v in values
                    ]
                else:
                    value = [
                        "<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                            v.get("Link"),
                            v.get("Title"),
                            "style='font-style:oblique;'",
                            v.get("Status"),
                        )
                        for v in values
                    ]
                value = "<ul>{}</ul>".format("".join(value))

            prop = "{}_info".format(name.lower())

            res[prop] = value

        values = processed_data["Legal_Policies"].get("AdaptationPolicies", [])
        sorted_items = sorted(values, key=lambda i: i["Type"])
        _response = {}
        sorted_items = [
            x for x in sorted_items if x["Status"].endswith(("completed", "(adopted)"))
        ]
        for item in sorted_items:
            _type = item["Type"]
            _type = _type[3: _type.find("(")]
            if _type not in _response:
                _response[_type] = []
            _response[_type].append(item)

        value = ""
        for key in _response:
            data = _response[key]
            _value = [
                "<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                    v.get("Link"),
                    v["Title"].encode("ascii", "ignore").decode("ascii"),
                    "style='font-style:oblique;'",
                    v.get("Status"),
                )
                for v in data
            ]
            if len(_value):
                value += str("<span>") + key + str("</span>")
                value += str("<ul>") + str("").join(_value) + str("</ul>")
        res["mixed"] = value

        # import pdb; pdb.set_trace()
        res["nas_mixed"] = ""
        res["nap_mixed"] = ""
        res["sap_mixed"] = ""
        if values:
            # setup National adaptation policy - NAS, NAP and SAP
            # import pdb; pdb.set_trace()
            for name in ("NAS", "NAP", "SAP"):
                value = ""
                data = [c for c in values if "(" + name + ")" in c["Type"]]

                if name == "SAP":
                    value = [
                        "<li><a href='{0}'>{1}</a><p {5}>{3}</p>"
                        "<p {4}>{2}</p></li>".format(
                            v.get("Link"),
                            v.get("Title"),
                            v.get("Status"),
                            v.get("Sector"),
                            "style='font-style:oblique;'",
                            "style='font-weight:bold;'",
                        )
                        for v in data
                    ]
                else:
                    value = [
                        "<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                            v.get("Link"),
                            v.get("Title"),
                            "style='font-style:oblique;'",
                            v.get("Status"),
                        )
                        for v in data
                    ]
                if len(value):
                    value = "<ul>{}</ul>".format("".join(value))
                else:
                    value = ""

                prop = "{}_mixed".format(name.lower())

                res[prop] = value

        # setup Climate change impact and vulnerability assessments
        value = ""
        values = processed_data["National_Circumstances"].get("CC_IVA", [])
        if values:
            value = [
                "<li><a href='{}'>{}</a><p {}>{}</p></li>".format(
                    v.get("Link"),
                    v.get("Title"),
                    "style='font-style:oblique;'",
                    v.get("Status"),
                )
                for v in values
            ]
            value = "<ul>{}</ul>".format("".join(value))

        res["cciva_info"] = value

        # setup Adaptation portals and platforms
        value = ""
        try:
            values = processed_data["Contact"].get("CCIV_Portal_Platform", [])
        except:
            logger.info("EMPTY DATA 395")

        if values:
            value = [
                "<li><a href='{0}'>{1}</a><p {5}>{3}</p><p {4}>{2}</p></li>".format(
                    v.get("Website"),
                    v.get("Name"),
                    v.get("Status"),
                    v.get("Focus"),
                    "style='font-style:oblique;'",
                    "style='font-weight:bold;'",
                )
                for v in values
            ]
            value = "<ul>{}</ul>".format("".join(value))

            focus_vals = [
                f for focus in values for f in focus.get("Focus", "").split("; ")
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

        res = get_nap_nas(obj, text, country=obj.id.title().replace("-", " "))
        res["notreported"] = True

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

            res[child.id.title().replace("-", " ")] = [
                c_metadata,
                child.absolute_url(),
            ]

        self.request.response.setHeader("Content-type", "application/json")
        data = []
        for marker in _MARKERS:
            data.append(
                [
                    marker[1],
                    translate_text(
                        self.context,
                        self.request,
                        marker[1],
                        "eea.cca",
                        self.current_lang,
                    ),
                ]
            )

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
            value = "\n".join(text)
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
        # "United Kingdom",
        "Liechtenstein",
        "Norway",
        "Switzerland",
        "Turkey",
    ]

    def countries(self):
        objects = self.context.aq_parent.contentValues()

        return sorted(
            [
                x
                for x in objects
                if x.id.title().replace("-", " ") in self.available_countries
            ],
            key=lambda x: x.id.title().replace("-", " "),
        )

    def script_country_settings(self):
        context_titles = [
            x.id.title().replace("-", " ")
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


class ContextCountriesViewJson(BrowserView):
    def __call__(self):
        # used for heat_index map
        info = parse_csv("data/heat_index.csv")
        m = {}

        for line in info:
            if line["country_id"].strip():
                m[line["country_id"]] = line

        return json.dumps(m)


class CountryProfileData(BrowserView):
    template = ViewPageTemplateFile("pt/country-profile-2025.pt")

    def verify_country_name(self, country_name):
        if country_name.lower in ["turkiye"]:
            country_name = "Turkey"
        return country_name

    def get_processed_data(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']
        return processed_data

    def convert_web_int(self, text):
        if not text:
            return text

        _text = CCAWebIntelligentToHtmlConverter(text.strip())()

        # import pdb; pdb.set_trace()

        return _text

    def get_sub_national_websites(self):
        data = self.get_processed_data()

        if "Sub_National_Adaptation" not in list(data.keys()):
            return []
        data = data["Sub_National_Adaptation"]
        if "Sub_National_Websites" not in list(data.keys()):
            return []
        data = data["Sub_National_Websites"]

        return data

    def get_sub_national_publications(self):
        data = self.get_processed_data()

        if "Sub_National_Adaptation" not in list(data.keys()):
            return []
        data = data["Sub_National_Adaptation"]
        if "Sub_National_Publications" not in list(data.keys()):
            return []
        data = data["Sub_National_Publications"]

        for index in range(len(data)):
            data[index]["Title"] = data[index]["TitleEnglish"]
            data[index]["Url"] = data[index]["WebLink"]

        return data

    def get_sorted_affected_sectors_data(self):
        # items = self.processed_data['National_Circumstances'].get(
        #     'Afected_Sectors', [])
        # sorted_items = sorted(
        #     items,
        #     key=lambda i: (i['SectorTitle'], i['SectorDescribeIfOther'] if 'SectorDescribeIfOther' in i else '')
        # )

        items = self.processed_data.get("Key_Affected_Sectors", [])

        if not items:
            return []
        # for some countries if we have only one item, will return the item and not a array
        if "Id" in items:
            items = [items]

        sections = []
        unqiue_items = []
        for item in items:
            if item['SectorDescribe'] not in sections:
                sections.append(item['SectorDescribe'])
                unqiue_items.append(item)
        sorted_items = sorted(
            unqiue_items,
            key=lambda i: (i['SectorDescribe'], i['SectorDescribe']
                           if 'SectorDescribe' in i else '')
        )

        return sorted_items

    def get_sorted_action_measures_data(self):
        if not self.processed_data["Strategies_Plans"]:
            return None

        items = self.processed_data["Strategies_Plans"].get(
            "Action_Measures", [])

        sorted_items = sorted(
            items, key=lambda i: (i["KeyTypeMeasure"], i["subKTM"], i["Title"])
        )

        # import pdb
        # pdb.set_trace()
        return sorted_items

    def get_sorted_available_practices_data(self):
        if not self.processed_data["Cooperation_Experience"]:
            return None

        items = self.processed_data["Cooperation_Experience"].get(
            "AvailableGoodPractices", []
        )

        # import pdb
        # pdb.set_trace()
        for index, item in enumerate(items):
            if 'Title' not in item:
                data = item['DescribeGoodPractice'].split('\n')
                items[index]['Title'] = data[0]
                items[index]['DescribeGoodPractice'] = '\n'.join(data[1:])
        return items
        # TODO in 2025 for the moment we do not have title
        sorted_items = sorted(items, key=lambda i: i["Id"])
        # sorted_items = sorted(items, key=lambda i: i["Title"])

        return sorted_items

    def fix_link(self, link):
        """Fix links like www.website.com"""
        if link != "#" and "http" not in link:
            return "http://" + link

        return link

    def summary_table(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        # import pdb
        # pdb.set_trace()
        response = OrderedDict()

        if not processed_data["Legal_Policies"]:
            return {"keys": [], "items": []}

        items = processed_data.get("Legal_Policies", []).get(
            "AdaptationPolicies", [])
        items = sorted(items, key=lambda x: x["Type"])

        for item in items:
            # # TODO CHECK perhaps we have to use Available as YES
            # if 'StatusId' not in item:
            #     continue
            typeName = item["Type"]
            item["Status"] = str(item["Status"])

            typeName = item["Type"]
            temp = typeName.split(":", 1)
            if len(temp) == 2:
                typeName = temp[1]
            typeName = typeName.strip()
            if typeName not in list(response.keys()):
                response[typeName] = []
            if len(item["Status"]) > 1 and item["Status"][1] == "-":
                item["Status"] = item["Status"][2:]
            response[typeName].append(
                {
                    "status": item["Status"],
                    "title": item["Title"],
                    "link": self.fix_link(item.get("Link", "#")),
                }
            )

        keys = list(response.keys())
        return {"keys": keys, "items": response}

    def hazards_table(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        response = {}
        countItems = {"Observed": 0, "Future": 0}
        items = (
            processed_data.get("Observed_Future_Climate_Hazards", [])
            .get("HazardsForm", [])[0]
            .get("Hazards", [])
        )
        # import pdb
        # pdb.set_trace()
# (Pdb) pp processed_data['Contact']['Website']

        if len(items) == 0:
            return items

        for item in items:
            occurence = item["Occurrence"]
            if occurence not in list(response.keys()):
                response[occurence] = {}
            group = item["Group"]
            if group == "SolidMass":
                group = "Solid mass"
            if group not in list(response[occurence].keys()):
                response[occurence][group] = {
                    "AC": {"hazards": [], "trend": [], "occurrences": []},
                    "CH": {"hazards": [], "trend": [], "occurrences": []},
                }
            accuteChronic = item["Type"]
            event = item["Event"]
            if occurence == "Future" and item["PatternValue"][0] == "0":
                continue
            if occurence == "Observed" and item["YesNo_Value"] == "NO":
                continue
            # if event not in response[occurence][group][accuteChronic]['hazards']:
            response[occurence][group][accuteChronic]["hazards"].append(
                item["Event"])
            # response[occurence][group][accuteChronic]["occurrences"].append(
            #     item["Occurrence"])
            # countItems[ group] += 1
            if occurence == "Future":
                response[occurence][group][accuteChronic]["trend"].append(
                    item["PatternValue"][2:]
                )

        observedHtml = ""
        for hazardType in response["Observed"]:
            countAC = len(response["Observed"][hazardType]["AC"]["hazards"])
            countCH = len(response["Observed"][hazardType]["CH"]["hazards"])
            observedHtml += (
                "<tr><td rowspan='"
                + str(max(1, countAC) + max(1, countCH))
                + "' class='bb1'>"
                + hazardType
                + "</td>"
            )
            observedHtml += (
                "<td rowspan='" + str(max(1, countAC)) +
                "' class='bb1'>Acute</td>"
            )
            if len(response["Observed"][hazardType]["AC"]["hazards"]):
                className = ' class="bb1"' if countAC == 1 else ""
                observedHtml += (
                    "<td"
                    + className
                    + ">"
                    + response["Observed"][hazardType]["AC"]["hazards"][0]
                    if countAC
                    else "" + "</td>"
                )
                # observedHtml += (
                #     "<td"
                #     + className
                #     + ">"
                #     + response["Observed"][hazardType]["AC"]["occurrences"][0]
                #     if countAC
                #     else "" + "</td>"
                # )
                observedHtml += "</tr>"
                hazards = response["Observed"][hazardType]["AC"]["hazards"][1:]
                # occurrences = response["Observed"][hazardType]["AC"]["occurrences"][1:]
                for idx in range(len(hazards)):
                    # import pdb; pdb.set_trace()
                    className = ' class="bb1"' if idx + \
                        1 == len(hazards) else ""
                    observedHtml += "<tr>"
                    observedHtml += (
                        "<td" + className + ">" +
                        hazards[idx] + "</td>"
                    )
                    # observedHtml += (
                    #     "<td" + className + ">"+occurrences[idx]+"</td>"
                    # )
                    observedHtml += "</tr>"
            else:
                observedHtml += "<td class='bb1'/><td class='bb1'/></tr>"

            observedHtml += "<tr>"
            observedHtml += (
                "<td class='bb1' rowspan='" +
                str(max(1, countCH)) + "'>Chronic</td>"
            )
            if len(response["Observed"][hazardType]["CH"]["hazards"]):
                # import pdb; pdb.set_trace()
                className = ' class="bb1"' if countCH == 1 else ""
                observedHtml += (
                    "<td"
                    + className
                    + ">"
                    + response["Observed"][hazardType]["CH"]["hazards"][0]
                    + "</td>"
                )
                # observedHtml += (
                #     "<td"
                #     + className
                #     + ">"
                #     + response["Observed"][hazardType]["CH"]["occurrences"][0]
                #     + "</td>"
                # )
                observedHtml += "</tr>"
                hazards = response["Observed"][hazardType]["CH"]["hazards"][1:]
                # occurrences = response["Observed"][hazardType]["CH"]["occurrences"][1:]
                for idx in range(len(hazards)):
                    className = ' class="bb1"' if idx + \
                        1 == len(hazards) else ""
                    observedHtml += "<tr>"
                    observedHtml += (
                        "<td" + className + ">" +
                        hazards[idx] + "</td>"
                    )
                    # observedHtml += (
                    #     "<td" + className + ">" + occurrences[idx] + "</td>"
                    # )
                    observedHtml += "</tr>"
            else:
                observedHtml += "<td class='bb1'/><td class='bb1'/></tr>"

        futureHtml = ""
        for hazardType in response["Future"]:
            countAC = len(response["Future"][hazardType]["AC"]["hazards"])
            countCH = len(response["Future"][hazardType]["CH"]["hazards"])
            futureHtml += (
                "<tr><td rowspan='"
                + str(max(1, countAC) + max(1, countCH))
                + "' class='bb1'>"
                + hazardType
                + "</td>"
            )
            futureHtml += (
                "<td rowspan=" + str(max(1, countAC)) +
                " class='bb1'>Acute</td>"
            )
            className = ' class="bb1"' if countAC <= 1 else ""
            futureHtml += (
                "<td"
                + className
                + ">"
                + response["Future"][hazardType]["AC"]["hazards"][0]
                if countAC
                else "" + "</td>"
            )
            futureHtml += (
                "<td"
                + className
                + ">"
                + response["Future"][hazardType]["AC"]["trend"][0]
                if countAC
                else "" + "</td>"
            )
            futureHtml += "</tr>"

            if countAC:
                hazards = response["Future"][hazardType]["AC"]["hazards"][1:]
                for idx in range(len(hazards)):
                    className = ' class="bb1"' if idx + \
                        1 == len(hazards) else ""
                    futureHtml += (
                        "<tr><td"
                        + className
                        + ">"
                        + response["Future"][hazardType]["AC"]["hazards"][idx + 1]
                        + "</td>"
                    )
                    futureHtml += (
                        "<td"
                        + className
                        + ">"
                        + response["Future"][hazardType]["AC"]["trend"][idx + 1]
                        + "</td></tr>"
                    )
            # else:
            #     futureHtml += "<td class='bb1'/><td class='bb1'/><tr>"

            futureHtml += "<tr>"
            futureHtml += (
                "<td rowspan=" + str(max(1, countCH)) +
                "  class='bb1'>Chronic</td>"
            )
            if countCH:
                className = ' class="bb1"' if countCH == 1 else ""
                futureHtml += (
                    "<td"
                    + className
                    + ">"
                    + response["Future"][hazardType]["CH"]["hazards"][0]
                    if countCH
                    else "" + "</td>"
                )
                futureHtml += (
                    "<td"
                    + className
                    + ">"
                    + response["Future"][hazardType]["CH"]["trend"][0]
                    if countCH
                    else "" + "</td>"
                )
                futureHtml += "</tr>"
                hazards = response["Future"][hazardType]["CH"]["hazards"][1:]
                for idx in range(len(hazards)):
                    className = ' class="bb1"' if idx + \
                        1 == len(hazards) else ""
                    futureHtml += (
                        "<tr><td"
                        + className
                        + ">"
                        + response["Future"][hazardType]["CH"]["hazards"][idx + 1]
                        + "</td>"
                    )
                    futureHtml += (
                        "<td"
                        + className
                        + ">"
                        + response["Future"][hazardType]["CH"]["trend"][idx + 1]
                        + "</td></tr>"
                    )
            else:
                futureHtml += "<td class='bb1'/><td class='bb1'/><tr>"

        return {
            "observedHtml": observedHtml,
            "futureHtml": futureHtml,
            "data": response,
        }

    def hazards_table_prev_version(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        response = {}
        items = (
            processed_data.get("Observed_Future_Climate_Hazards", [])
            .get("HazardsForm", [])[0]
            .get("Hazards", [])
        )
        # import pdb; pdb.set_trace()

        for item in items:
            occurence = item["Occurrence"]
            if occurence not in list(response.keys()):
                response[occurence] = {}
            group = item["Group"]
            if group not in list(response[occurence].keys()):
                response[occurence][group] = {}
            event = item["Event"]
            if occurence == "Future" and item["PatternValue"][0] == "0":
                continue
            if occurence == "Observed" and item["YesNo_Value"] == "NO":
                continue
            if event not in list(response[occurence][group].keys()):
                response[occurence][group][event] = []

            response[occurence][group][event].append(item)

        # import pdb; pdb.set_trace()

        keys = list(response.keys())
        keys.sort()
        return {"keys": keys, "items": response}

    def __call__(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        # import pdb
        # pdb.set_trace()
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        self.processed_data = processed_data
        # import pdb
        # pdb.set_trace()
        return self.template(
            country_data=processed_data,
            country_code=country_code,
            country_name=country_name,
        )

    def publications_websites(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        items = []
        response = []
        weblinks = []
        contact_data = processed_data.get("Contact", [])

        if "Publications" in contact_data:
            items = contact_data.get("Publications")
        else:
            for contact in contact_data:
                for publication in contact.get('Publications', []):
                    if publication.get('WebLink', None) and publication.get('WebLink', None) not in weblinks:
                        weblinks.append(publication.get('WebLink'))
                        items.append(publication)

        for item in items:
            line = {'Publisher': item.get('Publisher', ''), 'Title': item.get(
                'TitleEnglish', ''), 'Website': item.get('WebLink', '')}
            response.append(line)

        return response

    def contact_websites(self):
        country_name = self.verify_country_name(
            self.context.id.title().replace("-", " ")
        )
        country_code = get_country_code(country_name)

        processed_data = get_discodata_for_country(country_code)
        # [u'AT', u'BE', u'BG', u'CZ', u'DE', u'DK', u'EE', u'ES', u'FI',
        # u'GR', u'HR', u'HU', u'IE', u'IT', u'LT', u'LU', u'LV', u'MT',
        # u'NL', u'PL', u'PT', u'RO', u'SE', u'SI', u'SK', u'TR']

        items = []
        response = []
        weblinks = []
        contact_data = processed_data.get("Contact", [])

        if "Contact_General" in contact_data:
            items = contact_data.get("Contact_General")
        else:
            for contact in contact_data:
                for contact_general in contact.get('Contact_General', []):
                    if contact_general.get('Website', None) and contact_general.get('Website', None) not in weblinks:
                        weblinks.append(contact_general.get('Website'))
                        items.append(contact_general)

        for item in items:
            line = {'Organisation': item.get('Organisation', ''), 'Department': item.get(
                'Department', ''), 'Website': item.get('Website', '')}
            response.append(line)
        # pdb.set_trace()
        return response


class CountryProfileDataRaw(CountryProfileData):
    template = ViewPageTemplateFile("pt/country-profile-2025-raw.pt")
