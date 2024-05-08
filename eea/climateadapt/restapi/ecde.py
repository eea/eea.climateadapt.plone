# -*- coding: utf-8 -*-
import logging

from zope.component import getMultiAdapter
from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from eea.climateadapt.translation.utils import (
    TranslationUtilsMixin,
    get_current_language,
)
from plone import api
from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.interface import Interface, implementer

logger = logging.getLogger("eea.climateadapt")


@implementer(IExpandableElement)
@adapter(Interface, IEEAClimateAdaptInstalled)
class C3SIndicatorsOverview(TranslationUtilsMixin):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_ecde_context(self):
        layout = getattr(self.context.aq_inner.aq_self, "layout", None)
        if layout == "c3s_indicators_listing":
            return True

        # if "european-climate-data-explorer" in self.request["ACTUAL_URL"]:
        #     return True

        return False

    def get_indicators_data(self):
        current_lang = self.current_lang
        res = {"description": "", "items": []}

        # # url = self.request["ACTUAL_URL"]
        # category = url.split("/")[-2]
        category_id = self.context.getId().lower().replace("-", " ")
        c3s_theme = category_id.capitalize()

        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog.searchResults(
            portal_type="eea.climateadapt.c3sindicator", c3s_theme=c3s_theme
        )

        items = {}
        for brain in brains:
            if "/en/" not in brain.getURL():
                continue
            obj = brain.getObject()
            items[obj.title] = {"url": brain.getURL(), "obj": obj}

        current_lang = get_current_language(self.context, self.request)

        site = portal.get()
        base_folder = site["en"]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})

        if category_id not in datastore["data"]["themes"]:
            return {}

        res["description"] = datastore["data"]["themes"][category_id]["description"]

        for indicator in datastore["data"]["themes"][category_id]["apps"]:
            if indicator["title"] in items:
                obj = items[indicator["title"]]["obj"]
                if current_lang != "en":
                    try:
                        translations = TranslationManager(obj).get_translations()
                        if current_lang in translations:
                            obj = translations[current_lang]
                    except Exception:
                        logger.warning(
                            "At least one language is not published for %s",
                            obj.absolute_url(),
                        )
                res["items"].append(
                    {
                        "title": obj.title,
                        "url": obj.absolute_url(),
                    }
                )

        return res

    def __call__(self, expand=False):
        if self.is_ecde_context() is True:
            indicators_data = self.get_indicators_data()
            return {"c3s_indicators_listing": indicators_data}
        else:
            return {}


class C3SIndicatorsOverviewGet(Service):
    def reply(self):
        indicators = C3SIndicatorsOverview(self.context, self.request)
        return indicators()


@implementer(IExpandableElement)
@adapter(Interface, IEEAClimateAdaptInstalled)
class C3SIndicatorsData(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def is_ecde_context(self):
        if "european-climate-data-explorer" in self.request["ACTUAL_URL"]:
            return True
        return False

    def get_glossary(self):
        site = portal.get()
        # lg = get_current_language(self.context, self.request)
        lg = "en"
        base_folder = site[lg]["knowledge"]["european-climate-data-explorer"]
        datastore = IAnnotations(base_folder).get("c3s_json_data", {})

        if "glossary_table" in datastore["data"]:
            return datastore["data"]["glossary_table"]

        return ""

    def __call__(self, expand=False):
        if not self.is_ecde_context():
            return {}

        data_view = getMultiAdapter(
            (self.context, self.request), name="c3s_indicators_overview"
        )
        return {
            "c3s_indicators_glossary_table": self.get_glossary(),
            "c3s_indicators_overview": data_view(),
        }


class C3SIndicatorsGlossaryTableGet(Service):
    def reply(self):
        table = C3SIndicatorsData(self.context, self.request)
        return table()
