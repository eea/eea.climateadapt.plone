import json
import logging

from eea.climateadapt.translation.utils import translate_text
from plone.api.portal import get_tool
from Products.Five import BrowserView
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from collections import OrderedDict

from eea.climateadapt.vocabulary import (
    ipcc_category,
    aceitem_sectors_vocabulary,
    aceitem_climateimpacts_vocabulary,
)

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

logger = logging.getLogger("eea.climateadapt")


class Items(BrowserView):
    def __call__(self):
        """"""
        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_climateimpacts"
        )
        vocabulary_impacts = factory(self.context)
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary_sectors = factory(self.context)
        # 261447 - for case studies we have 6 more elements compared with other types
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_elements_case_study")
        vocabulary_elements = factory(self.context)

        results = {
            "type": "FeatureCollection",
            "metadata": {
                "generated": 1615559750000,
                "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson",
                "title": "Cliamte-Adapta arcgis items",
                "status": 200,
                "api": "1.10.3",
                "count": 10739,
            },
            "features": [],
            "filters": {'sectors': [], 'impacts': [], 'elements': [], 'measures': {}},
        }
        # Add available filters
        for term in vocabulary_sectors:
            results["filters"]['sectors'].append({"key": term.value, "value": term.title})
        for term in vocabulary_elements:
            results["filters"]['elements'].append({"key": term.value, "value": term.title})
        for term in vocabulary_impacts:
            results["filters"]['impacts'].append({"key": term.value, "value": term.title})

        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_key_type_measures"
        )
        vocabulary = factory(self.context)
        for term in vocabulary:
            temp = translate_text(self.context, self.request, term.title)
            titleSplit = temp.split(":")
            nameCategory = titleSplit[1].strip()
            if nameCategory not in results["filters"]['measures']:
                results["filters"]['measures'][nameCategory] = []
            results["filters"]['measures'][nameCategory].append(
                {"key": term.value, "value": titleSplit[2].strip()}
            )

        catalog = get_tool("portal_catalog")
        brains = catalog.searchResults(
            {
                "portal_type": [
                    "eea.climateadapt.casestudy",
                    "eea.climateadapt.adaptationoption",
                ],
                "path": "/cca/en",
                "review_state": "published",
            }
        )

        iPos = 0
        for brain in brains:
            obj = brain.getObject()
            if hasattr(obj, "geolocation") and obj.geolocation:
                list_key_type_measures = []
                list_ipcc_categories = []
                list_adaptation_options = []
                list_adaptation_options_links = []
                adaptation_options = obj.adaptationoptions
                for ao_related in adaptation_options:
                    try:
                        ao = ao_related.to_object
                        if hasattr(ao, "ipcc_category"):
                            for ipcc_category in ao.ipcc_category:
                                if ipcc_category not in list_ipcc_categories:
                                    list_ipcc_categories.append(ipcc_category)
                        if hasattr(ao, "key_type_measures"):
                            for key_type_measure in ao.key_type_measures:
                                if key_type_measure not in list_key_type_measures:
                                    list_key_type_measures.append(key_type_measure)
                        list_adaptation_options.append(ao.title)
                        list_adaptation_options_links.append(
                            "<a href='"
                            + ao.absolute_url_path()
                            + "'>"
                            + ao.title
                            + "</a>"
                        )
                    except:
                        """"""

                sectors_str = []
                impacts_str = []
                elements_str = []
                # import pdb
                # pdb.set_trace()
                for sector in obj.sectors:
                    try:
                        sectors_str.append(vocabulary_sectors.getTerm(sector).title)
                    except:
                        """"""
                for impact in obj.climate_impacts:
                    try:
                        impacts_str.append(vocabulary_impacts.getTerm(impact).title)
                    except:
                        """"""
                if obj.elements:
                    for element in obj.elements:
                        try:
                            elements_str.append(vocabulary_elements.getTerm(element).title)
                        except:
                            """"""

                if obj.geolocation.longitude == 0:
                    logger.info(
                        "Very south: %s %s %s",
                        obj.geolocation.longitude,
                        obj.geolocation.latitude,
                        brain.getURL(),
                    )

                long_description = ""
                if brain.long_description:
                    long_description = brain.long_description.raw
                results["features"].append(
                    {
                        "properties": {
                            "portal_type": obj.portal_type.replace(
                                "eea.climateadapt.", ""
                            ),
                            # "sectors": obj.sectors,
                            "sectors": "," + (",".join(obj.sectors)) + ",",
                            "elements": "," + (",".join(obj.elements)) if obj.elements else '' + ",",
                            "impacts": "," + (",".join(obj.climate_impacts)) + ",",
                            "ipccs": "," + (",".join(list_ipcc_categories)) + ",",
                            "ktms": "," + (",".join(list_key_type_measures)) + ",",
                            "adaptation_options": "<>".join(list_adaptation_options),
                            "adaptation_options_links": "<>".join(
                                list_adaptation_options_links
                            ),
                            "origin_adaptecca": 10
                            if "AdapteCCA" in obj.origin_website
                            else 20,
                            "sectors_str": ",".join(sectors_str),
                            "impacts_str": ",".join(impacts_str),
                            "elements_str": ",".join(elements_str),
                            "ipcc_categories_str": ",".join(list_ipcc_categories),
                            "title": obj.title,
                            "description": long_description,
                            "url": brain.getURL(),
                            "image": brain.getURL() + "/@@images/primary_photo/preview"
                            if obj.primary_photo
                            else "",
                        },
                        "geometry": {
                            "type": "Point",
                            # "coordinates": [geo.x, geo.y]
                            "svg": {"fill_color": "#009900"},
                            "color": "#009900",
                            "coordinates": [
                                obj.geolocation.longitude,
                                obj.geolocation.latitude,
                            ],
                        },
                    }
                )
                iPos = iPos + 1

        response = self.request.response
        response.setHeader("Content-type", "application/json")

        return json.dumps(results)


class Page(BrowserView):
    def get_climate_impacts(self):
        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_climateimpacts"
        )
        vocabulary = factory(self.context)
        response = []
        # response.append({"key": "", "value": "Filter by IMPACT"})
        for term in vocabulary:
            response.append({"key": term.value, "value": term.title})
        return response

    def get_sectors(self):
        factory = getUtility(IVocabularyFactory, "eea.climateadapt.aceitems_sectors")
        vocabulary = factory(self.context)
        response = []
        # response.append({"key": "", "value": "Filter by SECTOR"})
        for term in vocabulary:
            response.append({"key": term.value, "value": term.title})
        return response

    def get_ipcc_categories(self):
        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_ipcc_category"
        )
        vocabulary = factory(self.context)
        response = []
        # response.append({"key": "", "value": "Filter by IPCCS"})
        for term in vocabulary:
            response.append({"key": term.value, "value": term.title})
        return response

    def get_ipcc_categories2(self):
        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_ipcc_category"
        )
        vocabulary = factory(self.context)
        response = {}
        # import pdb; pdb.set_trace()
        # response.append({"key": "", "value": "Filter by IPCCS"})
        for term in vocabulary:
            temp = translate_text(self.context, self.request, term.title)
            titleSplit = temp.split(":")
            if titleSplit[0] not in response:
                response[titleSplit[0]] = []
            response[titleSplit[0]].append(
                {"key": term.value, "value": titleSplit[1].strip()}
            )
            # response.append({"key": term.value, "value": term.title})
        return response

    def get_key_type_measures(self):
        factory = getUtility(
            IVocabularyFactory, "eea.climateadapt.aceitems_key_type_measures"
        )
        vocabulary = factory(self.context)
        response = OrderedDict()
        # import pdb; pdb.set_trace()
        # response.append({"key": "", "value": "Filter by IPCCS"})
        for term in vocabulary:
            temp = translate_text(self.context, self.request, term.title)
            titleSplit = temp.split(":")
            if titleSplit[1] not in response:
                response[titleSplit[1]] = []
            response[titleSplit[1]].append(
                {"key": term.value, "value": titleSplit[0].strip()+': '+titleSplit[2].strip()}
            )
            # response.append({"key": term.value, "value": term.title})
        return response
