import logging
from collections import OrderedDict

from plone import api
from plone.api import content, portal
from eea.climateadapt.translation.utils import (
    TranslationUtilsMixin,
    get_current_language,
    translate_text,
)
from plone.app.multilingual.manager import TranslationManager
from Products.CMFPlone.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations

logger = logging.getLogger("eea.climateadapt")


class C3sIndicatorsOverview(BrowserView, TranslationUtilsMixin):
    """Overview page for indicators. Registered as @@c3s_indicators_overview

    To be used from inside a collective.cover
    """

    @property
    def indicators(self):
        brains = content.find(portal_type="eea.climateadapt.c3sindicator")
        return [b.getObject() for b in brains]

    def json_indicator_page_to_url(self, json_indicator_page):
        """Given an indicator html page URL, it resolves to an imported indicator"""
        html_page = json_indicator_page.split("/")[-1]
        for iid, info in list(self.data.get("indicators", {}).items()):
            if info["overviewpage"] == html_page:
                for indicator in self.indicators:
                    if indicator.c3s_identifier == info["identifier"]:
                        return indicator.absolute_url()

    @property
    def data(self):
        site = portal.get()
        lg = get_current_language(self.context, self.request)
        # lg = "en"
        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        return datastore.get("data", {})

    def get_categories(self):
        site = portal.get()
        lg = get_current_language(self.context, self.request)
        # lg = "en"
        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        data_overview_page = datastore["data"]["overview_page"]

        response = []
        # hazard_type_order = data_overview_page['hazard_type_order']
        hazard_type_order = (
            data_overview_page["hazard_type_order_left"]
            + data_overview_page["hazard_type_order_right"]
        )
        # hazard_type_order.append(['Other'])

        for index, main_category in enumerate(data_overview_page["category_order"]):
            if main_category in data_overview_page["hazard_list"]:
                category_data = data_overview_page["hazard_list"][main_category]

                subcategories = hazard_type_order[index]
                res = []
                for subcategory in subcategories:
                    if subcategory in category_data:
                        res.append((subcategory, category_data[subcategory]))
                response.append({"name": main_category, "data": res})

        return response

    def get_overview_columns(self):
        site = portal.get()
        lang = self.current_lang
        lg = "en"

        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        overview_page = datastore["data"]["overview_page"]
        response = {"left": [], "right": []}

        catalog = getToolByName(site, "portal_catalog")
        if "hazard_list_language" not in overview_page:
            overview_page["hazard_list_language"] = {}
        if lang not in overview_page["hazard_list_language"]:
            overview_page["hazard_list_language"][lang] = {}

            for category in overview_page["hazard_list"]:
                if category not in overview_page["hazard_list_language"][lang]:
                    overview_page["hazard_list_language"][lang][category] = {}
                for hazard in overview_page["hazard_list"][category]:
                    if (
                        hazard
                        not in overview_page["hazard_list_language"][lang][category]
                    ):
                        overview_page["hazard_list_language"][lang][category][
                            hazard
                        ] = []
                    for index, item in enumerate(
                        overview_page["hazard_list"][category][hazard]
                    ):
                        c3s_identifier = None
                        # print(item['title'])
                        for c3s_identifier_ in datastore["data"]["indicators"]:
                            # print("  "+c3s_identifier_)
                            # print("  "+datastore["data"]["indicators"][c3s_identifier_]["page_title"])
                            if (
                                datastore["data"]["indicators"][c3s_identifier_][
                                    "page_title"
                                ]
                                == item["title"]
                            ):
                                c3s_identifier = c3s_identifier_
                                # print("  --> FOUND")
                                break
                        if c3s_identifier:
                            query = {
                                "portal_type": "eea.climateadapt.c3sindicator",
                                "c3s_identifier": c3s_identifier,
                                "path": "/cca/" + lang + "/metadata",
                            }
                            brains = catalog.searchResults(query)
                            for brain in brains:
                                logger.info("C3S %s LNG %s", c3s_identifier, lang)
                                logger.info(
                                    "C3S %s URL %s",
                                    brain.getObject().c3s_identifier,
                                    brain.getURL(),
                                )

                                if c3s_identifier != brain.getObject().c3s_identifier:
                                    continue
                                if "/" + lang + "/" not in brain.getURL():
                                    continue
                                # overview_page['hazard_list'][category][hazard][index]['title'] = brain.getObject().title
                                # overview_page['hazard_list'][category][hazard][index]['url'] = brain.getURL()
                                overview_page["hazard_list_language"][lang][category][
                                    hazard
                                ].append(
                                    {
                                        "title": brain.getObject().title,
                                        "url": brain.getURL(),
                                    }
                                )
                                logger.info("LANG %s URL %", lang, brain.absolute_url())

                        else:
                            print(("Not found: " + item["title"]))

        for side in response:
            for cindex, category in enumerate(overview_page["category_order_" + side]):
                if category in overview_page["hazard_list"]:
                    category_index = len(response[side])
                    response[side].insert(
                        category_index, {"name": category, "items": []}
                    )

                    hazards = overview_page["hazard_type_order_" + side][cindex]
                    for hazard in hazards:
                        if hazard in overview_page["hazard_list"][category]:
                            len_hazard = len(response[side][category_index]["items"])
                            response[side][category_index]["items"].insert(
                                len_hazard,
                                {
                                    "name": hazard,
                                    "items": overview_page["hazard_list_language"][
                                        lang
                                    ][category][hazard],
                                },
                            )

        return response

    def get_overview_table(self):
        site = portal.get()
        lang = self.current_lang
        lg = "en"
        catalog = getToolByName(site, "portal_catalog")

        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        data = datastore["data"]["overview_table"]
        response = OrderedDict()

        for hazard_category in list(data.keys()):
            response[hazard_category] = {"types": OrderedDict(), "total_indicators": 0}
            for hazard_type in list(data[hazard_category].keys()):
                response[hazard_category]["types"][hazard_type] = []
                for indicator in data[hazard_category][hazard_type]:
                    c3s_identifier = indicator["identifier"]
                    # import pdb; pdb.set_trace()
                    query = {
                        "portal_type": "eea.climateadapt.c3sindicator",
                        "c3s_identifier": c3s_identifier,
                        "path": "/cca/" + lang + "/metadata",
                    }
                    if "cca_title" not in indicator:
                        indicator["cca_title"] = indicator["indicator_text"]
                    brains = catalog.searchResults(query)
                    indicator["cca_url"] = "#"
                    for brain in brains:
                        if c3s_identifier != brain.getObject().c3s_identifier:
                            continue
                        if "/" + lang + "/" not in brain.getURL():
                            continue
                        indicator["cca_url"] = brain.getURL()
                        indicator["cca_title"] = brain.getObject().title
                    response[hazard_category]["types"][hazard_type].append(indicator)
                    response[hazard_category]["total_indicators"] += 1

        responseHtml = str(
            "<thead>"
            "<tr>"
            "<th>"
            + translate_text(self.context, self.request, "Hazard category", "eea.cca")
            + "</th>"
            "<th>"
            + translate_text(self.context, self.request, "Hazard type", "eea.cca")
            + "</th>"
            "<th>"
            + translate_text(self.context, self.request, "Indicator", "eea.cca")
            + "</th>"
            # "<th>"
            # + translate_text(self.context, self.request,
            #                  "Zip download", "eea.cca")
            # + "</th>"
            "</tr>"
            "</thead>"
            "<tbody>"
        )
        for _category in response.keys():
            responseHtml += str("<tr>")
            responseHtml += (
                str('<td rowspan="')
                + str(response[_category]["total_indicators"])
                + '">'
                + translate_text(self.context, self.request, _category, "eea.cca")
                + str("</td>")
            )
            for i, _type in enumerate(response[_category]["types"].keys()):
                if i > 0:
                    responseHtml += str("<tr>")
                responseHtml += (
                    str('<td rowspan="')
                    + str(len(response[_category]["types"][_type]))
                    + '">'
                    + translate_text(self.context, self.request, _type, "eea.cca")
                    + str("</td>")
                )
                for j, indicator in enumerate(response[_category]["types"][_type]):
                    if j > 0:
                        responseHtml += str("<tr>")
                    responseHtml += (
                        str('<td><a href="')
                        + indicator["cca_url"]
                        + str('">')
                        + indicator["cca_title"]
                        + str("</a></td>")
                    )
                    # responseHtml += (
                    #     str('<td><a href="')
                    #     + indicator["zip_url"]
                    #     + str('">')
                    #     + translate_text(
                    #         self.context, self.request, "Download", "eea.cca"
                    #     )
                    #     + str("</a></td>")
                    # )
                    responseHtml += str("</tr>")

        return responseHtml + str("</tbody>")

    def get_disclaimer(self):
        site = portal.get()
        lg = get_current_language(self.context, self.request)
        # lg = 'en'
        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        return datastore["data"]["html_pages"]["disclaimer"]["page_text"]

    def get_glossary_table(self):
        site = portal.get()
        lg = get_current_language(self.context, self.request)
        # lg = 'en'
        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        if "glossary_table" in datastore["data"]:
            return datastore["data"]["glossary_table"]
        return ""

    def __call__(self):
        return self.index()


class C3sIndicatorsListing(BrowserView, TranslationUtilsMixin):
    """Listing of indicators for a category (theme) page.

    Registered as @@c3s_indicators_listing

    TODO: to be refactored according to the changes done in the restapi/ecde.py module
    """

    def __init__(self, context, request):
        # Each view instance receives context and request as construction parameters
        self.context = context
        self.request = request

    def list(self):
        res = {"description": "", "items": []}

        url = self.request["ACTUAL_URL"]
        category = url.split("/")[-1]
        category_id = category.lower().replace("-", " ")
        # category_path = category.lower()

        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(
            portal_type="eea.climateadapt.c3sindicator", c3s_theme=category.capitalize()
        )

        items = {}
        for brain in brains:
            if "/en/" not in brain.getURL():
                continue
            obj = brain.getObject()
            items[obj.title] = {"url": brain.getURL(), "obj": obj}

        site = portal.get()
        # lg = get_current_language(self.context, self.request) - KeyError: 'data'
        base_folder = site["en"]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})
        res["description"] = datastore["data"]["themes"][category_id]["description"]

        for indicator in datastore["data"]["themes"][category_id]["apps"]:
            if indicator["title"] in items:
                obj = items[indicator["title"]]["obj"]
                if self.current_lang != "en":
                    try:
                        translations = TranslationManager(obj).get_translations()
                        if self.current_lang in translations:
                            obj = translations[self.current_lang]
                    except:
                        logger.info(
                            "At least one language is not published for ".obj.absolute_url()
                        )
                res["items"].append(
                    {
                        "title": obj.title,
                        "url": obj.absolute_url(),
                    }
                )

        return res
