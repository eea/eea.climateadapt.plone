import json
import urllib
from collections import namedtuple

from eea.climateadapt.translation.utils import (TranslationUtilsMixin,
                                                translate_text)
from plone.api.portal import get_tool
from Products.Five.browser import BrowserView


Section = namedtuple("Section", ["title", "count", "link", "icon_class"])

SEARCH_TYPES_ICONS = [
    # ("MEASURE", "Adaptation options", "fa-cogs"),
    # ("ACTION", "Case studies", "fa-file-text-o"),
    ("GUIDANCE", "Guidance", "fa-compass"),
    ("INDICATOR", "Indicators", "fa-area-chart"),
    ("INFORMATIONSOURCE", "Information portals", "fa-info-circle"),
    # ("MAPGRAPHDATASET", "Maps, graphs and datasets"),       # replaced by
    # video
    ("VIDEO", "Videos", "fa-file-video-o"),
    ("ORGANISATION", "Organisations", "fa-sitemap"),
    ("DOCUMENT", "Publications and reports", "fa-newspaper-o"),
    ("RESEARCHPROJECT", "Research and knowledge projects", "research-icon"),
    ("TOOL", "Tools", "fa-wrench"),
]

class Urban(BrowserView, TranslationUtilsMixin):

    # TODO: implement cache using eea.cache
    # @cache
    def _make_link(self, search_type):
        t = {
            u"function_score": {
                u"query": {
                    u"bool": {
                        u"filter": {
                            u"bool": {
                                u"must": [
                                    {u"bool": {u"should":[{u"term": {u"typeOfData": search_type}}]}},
                                    {u"bool": {u"should":[{u"term": {u"sectors": "Urban"}}]}},
                                ]
                            }
                        },
                    }
                }
            }
        }

        base_query = "/{0}/data-and-downloads/?lang={0}&source=".format(
            self.current_lang)
        q = {"query": t}
        l = base_query + urllib.quote(json.dumps(q))

        return l

    def sections(self):
        catalog = get_tool("portal_catalog")
        counts = {}
        metadata = self.context.restrictedTraverse("en/metadata")
        path = "/".join(metadata.getPhysicalPath())

        for search_type, _x, _y in SEARCH_TYPES_ICONS:
            count = len(
                catalog.searchResults(
                    search_type=search_type,
                    sectors="URBAN",
                    review_state="published",
                    path={"query": path, "depth": 10},
                )
            )
            counts[search_type] = count

        tmp_types = []
        for data in SEARCH_TYPES_ICONS:
            data = list(data)
            data[1] = translate_text(self.context, self.request, data[1], 'eea.cca')
            tmp_types.append(data)
        return [
            Section(x[1], counts.get(x[0], 0), self._make_link(x[1]), x[2])
            #for x in SEARCH_TYPES_ICONS
            for x in tmp_types
        ]


class Forest(BrowserView, TranslationUtilsMixin):

    # TODO: implement cache using eea.cache
    # @cache
    def _make_link(self, search_type):
        t = {
            u"function_score": {
                u"query": {
                    u"bool": {
                        u"filter": {
                            u"bool": {
                                u"must": [
                                    {u"bool": {u"should":[{u"term": {u"typeOfData": search_type}}]}},
                                    {u"bool": {u"should":[{u"term": {u"sectors": "Forestry"}}]}},
                                ]
                            }
                        },
                    }
                }
            }
        }

        base_query = "/{0}/data-and-downloads/?lang={0}&source=".format(
            self.current_lang)
        q = {"query": t}
        l = base_query + urllib.quote(json.dumps(q))

        return l

    def sections(self):
        catalog = get_tool("portal_catalog")
        counts = {}
        metadata = self.context.restrictedTraverse("en/metadata")
        path = "/".join(metadata.getPhysicalPath())

        for search_type, _x, _y in SEARCH_TYPES_ICONS:
            count = len(
                catalog.searchResults(
                    search_type=search_type,
                    sectors="URBAN",
                    review_state="published",
                    path={"query": path, "depth": 10},
                )
            )
            counts[search_type] = count

        tmp_types = []
        for data in SEARCH_TYPES_ICONS:
            data = list(data)
            data[1] = translate_text(self.context, self.request, data[1], 'eea.cca')
            tmp_types.append(data)
        return [
            Section(x[1], counts.get(x[0], 0), self._make_link(x[1]), x[2])
            #for x in SEARCH_TYPES_ICONS
            for x in tmp_types
        ]
