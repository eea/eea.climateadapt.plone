from collections import namedtuple

from eea.climateadapt.config import ACEID_TO_SEARCHTYPE
# from eea.climateadapt.translation.utils import (TranslationUtilsMixin,
#                                                 filters_to_query,
#                                                 translate_text)
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

# TODO add TranslationUtilsMixin to inheritance
class Urban(BrowserView):
    def main_link(self):
        search_type = "Adaptation option"
        args = [
            ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
            ('cca_adaptation_sectors.keyword', "Urban"),
        ]
        # TODO fix query
        # query = filters_to_query(args)
        query = ''
        link = "/{0}/data-and-downloads/?{1}".format(self.current_lang, query)
        return link

    # TODO: implement cache using eea.cache
    # @cache
    def _make_link(self, search_type):
        args = [
            ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
            ('cca_adaptation_sectors.keyword', "Urban"),
        ]
        # TODO fix query
        # query = filters_to_query(args)
        query = ''
        link = "/{0}/data-and-downloads/?{1}".format(self.current_lang, query)

        return link

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
            # TODO fix translation
            # data[1] = translate_text(self.context, self.request, data[1], 'eea.cca')
            tmp_types.append(data)

        return [
            Section(title, counts.get(aceid, 0), self._make_link(aceid), icon)
            # for x in SEARCH_TYPES_ICONS
            for (aceid, title, icon) in tmp_types
        ]


# TODO add TranslationUtilsMixin to inheritance
class Forest(BrowserView):
    def main_link(self):
        search_type = "Adaptation option"
        args = [
            ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
            ('cca_adaptation_sectors.keyword', "Forestry"),
        ]
        # TODO fix query
        # query = filters_to_query(args)
        query = ''
        link = "/{0}/data-and-downloads/?{1}".format(self.current_lang, query)
        return link
        # return "/en/data-and-downloads/?lang=en&source=%7B%22query%22%3A%20%7B%22function_score%22%3A%20%7B%22query%22%3A%20%7B%22bool%22%3A%20%7B%22filter%22%3A%20%7B%22bool%22%3A%20%7B%22must%22%3A%20%5B%7B%22bool%22%3A%20%7B%22should%22%3A%20%5B%7B%22term%22%3A%20%7B%22typeOfData%22%3A%20%22Adaptation%20options%22%7D%7D%5D%7D%7D%2C%20%7B%22bool%22%3A%20%7B%22should%22%3A%20%5B%7B%22term%22%3A%20%7B%22sectors%22%3A%20%22Forestry%22%7D%7D%5D%7D%7D%5D%7D%7D%7D%7D%7D%7D%7D"

    # TODO: implement cache using eea.cache
    # @cache
    def _make_link(self, search_type):
        args = [
            ('objectProvides', ACEID_TO_SEARCHTYPE.get(search_type) or search_type),
            ('cca_adaptation_sectors.keyword', "Forestry"),
        ]
        # TODO fix query
        # query = filters_to_query(args)
        query = ''
        link = "/{0}/data-and-downloads/?{1}".format(self.current_lang, query)

        return link

    def sections(self):
        catalog = get_tool("portal_catalog")
        counts = {}
        metadata = self.context.restrictedTraverse("en/metadata")
        path = "/".join(metadata.getPhysicalPath())

        for search_type, _x, _y in SEARCH_TYPES_ICONS:
            count = len(
                catalog.searchResults(
                    search_type=search_type,
                    sectors="FORESTRY",
                    review_state="published",
                    path={"query": path, "depth": 10},
                )
            )
            counts[search_type] = count

        tmp_types = []
        for data in SEARCH_TYPES_ICONS:
            data = list(data)
            # TODO fix translation
            # data[1] = translate_text(self.context, self.request, data[1], 'eea.cca')
            tmp_types.append(data)

        return [
            Section(title, counts.get(aceid, 0), self._make_link(aceid), icon)
            # for x in SEARCH_TYPES_ICONS
            for (aceid, title, icon) in tmp_types
        ]
