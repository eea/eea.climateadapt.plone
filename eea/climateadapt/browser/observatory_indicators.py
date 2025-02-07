import logging

from plone.api.portal import get_tool
from Products.Five import BrowserView

from eea.climateadapt.translation.utils import TranslationUtilsMixin

# from eea.climateadapt.vocabulary import _origin_website
# from zope.component import getUtility
# import lxml.html
# from zope.schema.interfaces import IVocabularyFactory

logger = logging.getLogger("eea.climateadapt")


class ObservatoryIndicators(BrowserView, TranslationUtilsMixin):
    def map_origin_wesite(self, name):
        if name == "Lancet Countdown":
            return "Lancet Countdown in Europe"
        if name == "C3S":
            return "Copernicus (C3S)"
        return name

    def get_variable_from_query(self, variable):
        request = self.request
        if "PARENT_REQUEST" not in request:
            return None
        if variable not in request["PARENT_REQUEST"].form:
            return None
        return request["PARENT_REQUEST"].form[variable]

    def get_selected_origin_websites(self):
        return self.get_variable_from_query("origin_website")

    def get_selected_search(self):
        return self.get_variable_from_query("search")

    def get_origin_websites(self):
        catalog = get_tool("portal_catalog")
        origin_website = []
        search_params = {
            "path": "/cca/" + self.current_lang,
            "portal_type": [
                "eea.climateadapt.indicator",
                "eea.climateadapt.c3sindicator",
            ],
            "include_in_observatory": "True",
            "review_state": "published",
        }
        brains = catalog.searchResults(search_params)
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj, "origin_website"):
                for origin_name in obj.origin_website:
                    if origin_name not in origin_website:
                        origin_website.append(origin_name)
        origin_website.sort()
        return [[v, self.map_origin_wesite(v)] for v in origin_website]

    def get_search_params(self):
        search_params = {
            "path": "/cca/" + self.current_lang,
            "portal_type": [
                "eea.climateadapt.indicator",
                "eea.climateadapt.c3sindicator",
            ],
            "include_in_observatory": "True",
            "review_state": "published",
        }
        selected_origin = self.get_selected_origin_websites()
        selected_search = self.get_selected_search()
        if selected_search:
            search_params["SearchableText"] = selected_search
        if selected_origin:
            search_params["origin_website"] = selected_origin
        return search_params

    def get_data(self):
        catalog = get_tool("portal_catalog")
        items = []
        health_impacts = {
            "Heat": {
                "value": 0,
                "icon": "fa fa-area-chart",
                "print": self.get_i18n_for_text("Heat"),
            },
            "Droughts and floods": {
                "value": 0,
                "icon": "fa fa-compass",
                "print": self.get_i18n_for_text("Droughts and floods"),
            },
            "Climate-sensitive diseases": {
                "value": 0,
                "icon": "fa fa-info-circle",
                "print": self.get_i18n_for_text("Climate-sensitive diseases"),
            },
            "Air pollution and aero-allergens": {
                "value": 0,
                "icon": "fa fa-file-video-o",
                "print": self.get_i18n_for_text("Air pollution and aero-allergens"),
            },
            "Wildfires": {
                "value": 0,
                "icon": "fa fa-wrench",
                "print": self.get_i18n_for_text("Wildfires"),
            },
        }
        search_params = self.get_search_params()
        brains = catalog.searchResults(
            search_params, sort_on="sortable_title", sort_order="ascending"
        )
        for brain in brains:
            obj = brain.getObject()
            origin_website = ""
            if hasattr(obj, "origin_website"):
                origin_website = ", ".join(obj.origin_website)
            for key in health_impacts:
                if key in obj.health_impacts:
                    health_impacts[key]["value"] += 1

            if obj.publication_date is not None:
                items.append(
                    {
                        "title": obj.title,
                        "id": brain.UID,
                        "url": brain.getURL(),
                        "origin_websites": self.map_origin_wesite(origin_website),
                        "health_impacts_list": " ".join(
                            [
                                impact.lower().replace(" ", "_")
                                for impact in obj.health_impacts
                            ]
                        ),
                        "year": obj.publication_date.year,
                    }
                )

        return {"items": items, "health_impacts": health_impacts}
