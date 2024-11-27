""" A view that can be embeded in a tile.
It renders a search "portlet" for Ace content
"""

import logging
from collections import namedtuple

# from AccessControl import Unauthorized
# from collective.cover.interfaces import ICoverUIDsProvider
# from collective.cover.tiles.base import (IPersistentCoverTile,
#                                          PersistentCoverTile)
# from collective.cover.tiles.list import IListTile
from eea.climateadapt import MessageFactory as _
# from eea.climateadapt.catalog import get_aceitem_description
from eea.climateadapt.config import ACEID_TO_SEARCHTYPE
# from eea.climateadapt.translation.utils import (TranslationUtilsMixin,
#                                                 filters_to_query,
#                                                 get_current_language)
from eea.climateadapt.vocabulary import (BIOREGIONS, REMAPED_BIOREGIONS, _climateimpacts,
                                         _datatypes, _elements,
                                         _origin_website, _sectors,
                                         ace_countries_dict)
# from plone import api
# from plone.api import portal
# from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.memoize import view
# from plone.tiles.interfaces import ITileDataManager
# from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.CatalogTool import sortable_title
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.widget import StaticWidgetAttribute
from zope.component.hooks import getSite
# from zope.interface import implements
from zope.schema import Bool, Choice, Dict, Int, List, TextLine
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


ORIGIN_WEBSITES = dict(_origin_website)
CLIMATE_IMPACTS = dict(_climateimpacts)
COUNTRIES = ace_countries_dict
DATATYPES = dict(_datatypes)
ELEMENTS = dict(_elements)
SECTORS = dict(_sectors)

logger = logging.getLogger("eea.climateadapt")


# class ISearchAceContentTile(IPersistentCoverTile):

#     title = TextLine(
#         title="Title",
#         required=False,
#     )

#     search_text = TextLine(
#         title="Search Text",
#         required=False,
#         default="",
#     )

#     origin_website = List(
#         title="Origin website",
#         required=False,
#         value_type=Choice(
#             vocabulary='eea.climateadapt.origin_website'
#         ),
#     )

#     search_type = List(
#         title="Aceitem type",
#         required=False,
#         value_type=Choice(
#             vocabulary="eea.climateadapt.search_types_vocabulary",
#         ),
#     )

#     element_type = List(
#         title="Element type",
#         required=False,
#         value_type=Choice(
#             vocabulary="eea.climateadapt.element_types_vocabulary",
#         ),
#     )

#     sector = List(
#         title="Sector",
#         required=False,
#         value_type=Choice(
#             vocabulary="eea.climateadapt.aceitems_sectors",
#         ),
#     )

#     special_tags = List(
#         title="Special tags",
#         required=False,
#         value_type=Choice(vocabulary="eea.climateadapt.special_tags"),
#     )

#     countries = List(
#         title="Countries",
#         required=False,
#         value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
#     )

#     macro_regions = List(
#         title="Macro-Transnational Regions",
#         required=False,
#         value_type=Choice(vocabulary="eea.climateadapt.regions"),
#     )

#     bio_regions = List(
#         title="Biogeographical Regions",
#         required=False,
#         value_type=Choice(vocabulary="eea.climateadapt.bioregions"),
#     )

#     funding_programme = Choice(
#         vocabulary="eea.climateadapt.funding_programme",
#         title="Funding programmes",
#         required=False,
#     )

#     nr_items = Int(
#         title="Nr of items to show",
#         required=True,
#         default=5,
#     )


KEYWORD_INDEXES = ["search_type", "elements", "sectors"]


class AceTileMixin(object):
    """Mixin class for ace search/relevant content tiles"""

    @property
    def catalog(self):
        catalog = getToolByName(self.context, "portal_catalog")

        return catalog

    def build_query(self):

        # lang = get_current_language(self.context, self.request)
        lang = 'en'
        query = {"review_state": "published", }     # "Language": lang

        # todo: do countries
        # map of {tile field: index name}
        map = {
            "origin_website": "origin_website",
            "search_type": "search_type",
            "element_type": "elements",
            "search_text": "SearchableText",
            "special_tags": "special_tags",
            "sector": "sectors",
            "countries": "countries",
            "macro_regions": "macro_regions",
            "bio_regions": "bio_regions",
            "funding_programme": "funding_programme",
            "language": "language",
        }

        sort_map = {
            "RATING": "rating",
            "NAME": "sortable_title",
            "MODIFIED": "modified",
            "EFFECTIVE": "effective",
        }

        sort = self.data.get("sortBy")

        if sort:
            query["sort_on"] = sort_map[sort]

            if sort in ("MODIFIED", "EFFECTIVE"):
                query["sort_order"] = "reverse"

        for setting_name, index_name in list(map.items()):
            setting = self.data.get(setting_name, "")

            if setting:
                if index_name in KEYWORD_INDEXES:  # and len(setting) > 1:
                    query[index_name] = {"query": setting, "operator": "or"}
                else:
                    if index_name == 'macro_regions':
                        regions = []
                        if 'Other Regions' in setting:
                            setting.append('Macaronesia')
                            setting.append('Caribbean Area')
                            setting.append('Amazonia')
                            setting.append('Anatolian')
                            setting.append('Indian Ocean Area')
                            regions.append('TRANS_MACRO_OUTERMOST')
                        for region_name in setting:
                            for k, v in list(BIOREGIONS.items()) + list(REMAPED_BIOREGIONS.items()):
                                if 'TRANS_MACRO' in k and v == region_name:
                                    regions.append(k)
                        query[index_name] = regions
                    else:
                        query[index_name] = setting

        # get rid of special_tags index, just use the SearchableText
        # the special_tags field is indexed into the SearchableText
        st = self.data.get("special_tags")

        if st:
            query.pop("special_tags", None)

            if isinstance(st, str):
                st = st.split(" ")
            words = query.pop("SearchableText", "").split(" ")
            query["SearchableText"] = " ".join(set(words + st))

        query['Language'] = lang
        # print('query in search_acecontent', query)

        return query

    def build_url(self, url, query, kw):
        """Build urls suitable for the EEA Search engine"""
        q = query.copy()
        q.update(kw)
        x = {}

        for index, v in list(q.items()):
            if v:
                if index not in ["sort_on", "sort_order"]:
                    if isinstance(v, (tuple, list)):
                        x[index] = v
                    else:
                        # keyword indexes appear ex:
                        #  'sectors': {'operator': 'or',
                        #              'query': [u'AGRICULTURE']}

                        if index in KEYWORD_INDEXES:
                            if isinstance(v, str):
                                x[index] = [v]
                            else:
                                x[index] = v["query"]
                        else:
                            x[index] = [v]

        terms = []

        # now that the "query" is built, map it to EEA Search format

        for k, v in list(x.items()):

            if k == "search_type":
                terms.append(('objectProvides',
                              [ACEID_TO_SEARCHTYPE.get(
                                  s, DATATYPES.get(s, s)) for s in v]))

            if k == "origin_website":
                terms.append(('cca_origin_websites.keyword', [
                             ORIGIN_WEBSITES[s] for s in v]))

            if k == "sectors":
                terms.append(('cca_adaptation_sectors.keyword', [
                             SECTORS[s] for s in v]))

            if k == "climate_impacts":
                terms.append(('cca_climate_impacts.keyword', [
                             CLIMATE_IMPACTS[s] for s in v]))

            if k == "elements":
                terms.append(('cca_adaptation_elements.keyword', [
                             ELEMENTS[s] for s in v]))

            if k == "countries":
                terms.append(('cca_geographic_countries.keyword', [
                             COUNTRIES[s] for s in v]))

            if k == "funding_programme":
                terms.append(('cca_funding_programme.keyword', [s for s in v]))

            if k == "language":
                terms.append(('language', [s for s in v]))

            if k == "macro_regions":
                temp_terms = []
                for s in v:
                    if 'TRANS_MACRO_' in s:
                        for key, val in list(BIOREGIONS.items()):
                            if 'TRANS_MACRO_' in key and key == s:
                                if val in self.list_of_other_regions():
                                    val = 'Other Regions'
                                temp_terms.append(val)
                    else:
                        temp_terms.append(s)

                terms.append(
                    ('cca_geographic_transnational_region.keyword', temp_terms))

            if k == "SearchableText":
                terms.append(('q', v))

        # query = filters_to_query(terms)
        query = ''

        return "{}{}".format(url, query)        # urllib.quote(json.dumps(q))

    def list_of_other_regions(self):
        resp = []
        resp.append('Macaronesia')
        resp.append('Caribbean Area')
        resp.append('Amazonia')
        resp.append('Anatolian')
        resp.append('Indian Ocean Area')

        return resp

    def sections(self):
        """Returns a list of (section name, section count, section_url)"""
        site = getSite()
        base_query = "/{0}/data-and-downloads/?language={0}&".format(
            self.current_lang)

        base = site.absolute_url() + base_query

        result = []

        _ace_types = dict(_datatypes)

        search_type = self.data.get("search_type")

        if search_type and len(search_type) == 1:
            # Special case when we want to show the results, like RelevantTile
            search_type = search_type[0]
            query = self.build_query()
            count = self.data.get("nr_items", 5)
            brains = self.catalog.searchResults(**query)
            url = self.build_url(base, query, {})
            r = (_ace_types[search_type], len(brains), url, brains[:count])
            result.append(r)

            return result

        # TODO: sync the links here to the index names and to the faceted
        # indexes
        query = self.build_query()

        element_type = self.data.pop("element_type", [])

        for typeid, typelabel in _datatypes:
            if search_type:
                if not (typeid in search_type):
                    continue
            q = query.copy()

            q.update({"search_type": typeid})

            if element_type:
                q.update({"elements": element_type})

            # 'sort_on': 'rating' causes wrong count - see #261745
            simplified_q = q.copy()
            if 'sort_on' in simplified_q:
                del simplified_q['sort_on']

            count = len(self.catalog.searchResults(**simplified_q))

            if count:
                # TODO: this append needs 4 items, not 3
                url = self.build_url(base, q, {})
                r = (
                    typelabel,
                    count,
                    url,
                    [],
                )
                result.append(r)

        return result

    def relevant_items(self):
        query = self.build_query()
        res = self.catalog.searchResults(**query)

        return res

    def relevant_all_items(self):
        # current_language = get_current_language(self.context, self.request)
        count = int(self.data.get("nr_items", 5)) or 5
        res = []

        combine = self.data.get("combine_results", False)

        if not combine:
            return []

        for item in self.relevant_items():
            try:
                # TODO: this needs to be removed as soon as possible. Performance issues
                obj = item.getObject()
            except KeyError:        # this is an indexing problem
                logger.warn(
                    "Object not found in relevant_all_items: %s", item.getURL())
                continue
            # if '/' + current_language + '/' not in item.getURL():
            #     item = self.translated_object(item)

            if not item:
                continue

            adapter = sortable_title(obj)
            st = adapter()
            o = Item(
                item.Title,
                item.Description,
                '',
                st,
                item.getURL(),
            )
            res.append(o)

        return res[:count]


# class SearchAceContentTile(PersistentCoverTile, AceTileMixin, TranslationUtilsMixin):
#     """Search Ace content tile
#     It shows links to the search page, for all aceitems_types.
#     """

#     implements(ISearchAceContentTile)

#     # available options:
#     # title
#     # search_text
#     # element_type
#     # sector
#     # special_tags
#     # countries

#     index = ViewPageTemplateFile("pt/search_acecontent.pt")

#     is_configurable = True
#     is_editable = True
#     is_droppable = False
#     short_name = "Search AceContent"

#     @ view.memoize
#     def is_empty(self):
#         return False

#     @ view.memoize
#     def accepted_ct(self):
#         """Return an empty list as no content types are accepted."""

#         return []


sortby_def = {
    "MODIFIED": "Last Modified",
    "EFFECTIVE": "Last Published",
    "NAME": "Alphabetical sorting",
}

sortbyterms = [SimpleTerm(value=k, token=k, title=v)
               for k, v in list(sortby_def.items())]
sortby_vocabulary = SimpleVocabulary(sortbyterms)


# class IRelevantAceContentItemsTile(ISearchAceContentTile):

#     show_share_btn = Bool(
#         title="Show the share button",
#         default=False,
#     )

#     combine_results = Bool(
#         title="Show listing results, in addition to assigned items",
#         default=False,
#     )

#     uuids = Dict(
#         title="Elements",
#         key_type=TextLine(),
#         value_type=Dict(
#             key_type=TextLine(),
#             value_type=TextLine(),
#         ),
#         required=False,
#     )

#     sortBy = Choice(
#         title="Sort order for results and assigned items",
#         vocabulary=sortby_vocabulary,
#     )

#     form.omitted("uuids")


Item = namedtuple("Item", ["Title", "Description",
                           "icons", "sortable_title", "url"])


# class RelevantAceContentItemsTile(PersistentCoverTile, AceTileMixin, TranslationUtilsMixin):
#     """Relevant AceItem content"""

#     implements(IRelevantAceContentItemsTile, IListTile)

#     short_name = "Relevant AceContent"

#     is_configurable = True
#     is_editable = True
#     is_droppable = True

#     index = ViewPageTemplateFile("pt/relevant_acecontent.pt")

#     view_more = True

#     @ property
#     def is_available(self):
#         return bool(list(self.items()) or self.assigned())

#     # def show_share_btn(self):
#     #     search_type = self.data.get('search_type')
#     #
#     #     if search_type in ['DOCUMENT', 'INFORMATIONSOURCE',
#     #                        'GUIDANCE', 'TOOL', 'REASEARCHPROJECT',
#     #                        'MEASURE', 'ORGANISATION']:
#     #
#     #         return True

#     @ view.memoize
#     def is_empty(self):
#         return False

#     def get_description(self, item):
#         # TODO: move this code to an indexer and a metadata column

#         adapter = get_aceitem_description(item)
#         try:
#             value = adapter()
#         except AttributeError:  # object doesn't have long_description
#             return ""

#         return value

#     @ view.memoize
#     def accepted_ct(self):
#         """Return accepted drag/drop content types for this tile."""

#         cca_types = [
#             "eea.climateadapt.adaptationoption",
#             "eea.climateadapt.aceproject",
#             "eea.climateadapt.casestudy",
#             "eea.climateadapt.guidancedocument",
#             "eea.climateadapt.c3sindicator",
#             "eea.climateadapt.indicator",
#             "eea.climateadapt.informationportal",
#             "eea.climateadapt.mapgraphdataset",
#             "eea.climateadapt.organisation",
#             "eea.climateadapt.publicationreport",
#             "eea.climateadapt.researchproject",
#             "eea.climateadapt.tool",
#             "eea.climateadapt.video",
#         ]

#         return cca_types + [
#             "Document",
#             "Folder",
#             "collective.cover.content",
#             "Page",
#             "Link",
#         ]

#     def view_more_url(self):
#         site = getSite()
#         base = site.absolute_url() + "/data-and-downloads?"

#         q = {
#             "elements": self.data.get("element_type"),
#             "search_type": self.data.get("search_type"),
#             "SearchableText": self.data.get("search_text") or "",
#         }

#         return self.build_url(base, q, {})

#         # "http://climate-adapt.eea.europa.eu/data-and-downloads?searchtext=obs-scen-gen&searchelements=OBSERVATIONS&searchtypes=DOCUMENT"
#         # return
#         # "%s/data-and-downloads?searchtext=%s&searchelements=%s&searchtypes=%s"
#         # % ( site.absolute_url(), search_text, element_type, search_type)

#     @ view.memoize
#     def icon_images(self):
#         root = portal.get()

#         if "tile_icons" not in root.objectIds():
#             return []

#         tile_icons = root["tile_icons"]

#         return tile_icons.objectValues()

#     def get_icons(self, obj):
#         special_tags = getattr(obj, "special_tags", []) or []
#         images = self.icon_images()
#         icons = [image for image in images if image.getId() in special_tags]

#         return icons

#     # @view.memoize
#     def items(self):
#         count = self.data.get("nr_items", 5) or 5
#         query = self.build_query()
#         res = self.catalog.searchResults(**query)

#         if len(res) < count:
#             self.view_more = False

#         items = res[:count]

#         return items

#     def all_items(self):
#         current_language = get_current_language(self.context, self.request)
#         # site = getSite()
#         # catalog = site.portal_catalog
#         res = []

#         for item in self.assigned():
#             if current_language != 'en':
#                 # import pdb; pdb.set_trace()
#                 item = self.translated_object(item)
#             #    translations = TranslationManager(item).get_translations()
#             #    if current_language not in translations:
#             #        continue
#             #    item = translations[current_language]
#             if not item:
#                 continue
#             adapter = sortable_title(item)
#             st = adapter()
#             o = Item(
#                 item.Title(),
#                 self.get_description(item),
#                 self.get_icons(item),
#                 st,
#                 item.absolute_url(),
#             )
#             res.append(o)

#         combine = self.data.get("combine_results", False)

#         if not combine:
#             if res:
#                 if self.data.get("sortBy", "") == "NAME":
#                     return sorted(res, key=lambda o: o.sortable_title)
#                 else:
#                     return res

#         for item in list(self.items()):
#             obj = item.getObject()
#             if '/'+current_language+'/' not in item.getURL():
#                 item = self.translated_object(item)

#             if not item:
#                 continue

#             adapter = sortable_title(obj)
#             st = adapter()
#             o = Item(
#                 item.Title,
#                 item.Description,
#                 self.get_icons(item),
#                 st,
#                 item.getURL(),
#             )
#             res.append(o)

#         return res

#     # @view.memoize
#     def assigned(self):
#         """Return the list of objects stored in the tile as UUID. If an UUID
#         has no object associated with it, removes the UUID from the list.
#         :returns: a list of objects.
#         """
#         # self.set_limit()

#         # always get the latest data
#         uuids = ITileDataManager(self).get().get("uuids", None)

#         results = list()

#         if uuids:
#             ordered_uuids = [(k, v) for k, v in list(uuids.items())]
#             ordered_uuids.sort(key=lambda x: x[1]["order"])

#             for uuid in [i[0] for i in ordered_uuids]:
#                 obj = uuidToObject(uuid)

#                 if obj:
#                     results.append(obj)

#                 else:
#                     # maybe the user has no permission to access the object
#                     # so we try to get it bypassing the restrictions
#                     catalog = api.portal.get_tool("portal_catalog")
#                     # brain = catalog.unrestrictedSearchResults(UID=uuid, review_state='published')
#                     brain = catalog.searchResults(
#                         UID=uuid, review_state='published')

#                     if not brain:
#                         # the object was deleted; remove it from the tile
#                         self.remove_item(uuid)
#                         logger.debug(
#                             "Nonexistent object {0} removed from " "tile".format(
#                                 uuid)
#                         )
#         return results

#     def populate_with_object(self, obj):
#         """Add an object to the list of items
#         :param obj: [required] The object to be added
#         :type obj: Content object
#         """
#         super(RelevantAceContentItemsTile, self).populate_with_object(obj)
#         # check permission
#         # uuids = ICoverUIDsProvider(obj).getUIDs()

#         # if uuids:
#         #     self.populate_with_uuids(uuids)

#     def populate_with_uuids(self, uuids):
#         """Add a list of elements to the list of items. This method will
#         append new elements to the already existing list of items
#         :param uuids: The list of objects' UUIDs to be used
#         :type uuids: List of strings
#         """

#         if not self.isAllowedToEdit():
#             raise Unauthorized(
#                 "You are not allowed to add content to this tile")
#         # self.set_limit()
#         data_mgr = ITileDataManager(self)

#         old_data = data_mgr.get()

#         if old_data["uuids"] is None:
#             # If there is no content yet, just assign an empty dict
#             old_data["uuids"] = dict()

#         uuids_dict = old_data.get("uuids")

#         if not isinstance(uuids_dict, dict):
#             # Make sure this is a dict
#             uuids_dict = old_data["uuids"] = dict()

#         # if uuids_dict and len(uuids_dict) > self.limit:
#         #     # Do not allow adding more objects than the defined limit
#         #     return

#         order_list = [int(val.get("order", 0))
#                       for key, val in list(uuids_dict.items())]

#         if len(order_list) == 0:
#             # First entry
#             order = 0
#         else:
#             # Get last order position and increment 1
#             order_list.sort()
#             order = order_list.pop() + 1

#         for uuid in uuids:
#             if uuid not in list(uuids_dict.keys()):
#                 entry = dict()
#                 entry["order"] = str(order)
#                 uuids_dict[uuid] = entry
#                 order += 1

#         old_data["uuids"] = uuids_dict

#         # Whenever we insert an (or rearange), remove the alpha sort
#         old_data["sortBy"] = ""
#         data_mgr.set(old_data)

#     def replace_with_uuids(self, uuids):
#         """Replaces the whole list of items with a new list of items
#         :param uuids: The list of objects' UUIDs to be used
#         :type uuids: List of strings
#         """

#         if not self.isAllowedToEdit():
#             raise Unauthorized(
#                 "You are not allowed to add content to this tile")
#         data_mgr = ITileDataManager(self)
#         old_data = data_mgr.get()
#         # Clean old data
#         old_data["uuids"] = dict()
#         data_mgr.set(old_data)
#         # Repopulate with clean list
#         self.populate_with_uuids(uuids)

#     # @view.memoize
#     def get_uuid(self, obj):
#         """Return the UUID of the object.
#         :param obj: [required]
#         :type obj: content object
#         :returns: the object's UUID
#         """

#         return IUUID(obj, None)

#     def remove_item(self, uuid):
#         """Removes an item from the list
#         :param uuid: [required] uuid for the object that wants to be removed
#         :type uuid: string
#         """
#         super(RelevantAceContentItemsTile, self).remove_item(uuid)
#         # check permission
#         data_mgr = ITileDataManager(self)
#         old_data = data_mgr.get()
#         uuids = data_mgr.get()["uuids"]

#         if uuid in list(uuids.keys()):
#             del uuids[uuid]
#         old_data["uuids"] = uuids
#         data_mgr.set(old_data)


# class IFilterAceContentItemsTile(IRelevantAceContentItemsTile):
#     """Schema for filter aceitems
#     This is a results listing, but with two dropdowns to filter:
#     * climate impact
#     * adaptation sector
#     """


class IFilteringSchema(form.Schema):
    impact = Choice(
        title=_("Climate impact"),
        vocabulary="eea.climateadapt.aceitems_climateimpacts",
        required=False,
    )

    sector = Choice(
        title=_("Sector"),
        vocabulary="eea.climateadapt.aceitems_sectors",
        required=False,
    )

    key_type_measure = Choice(
        title=_("Key Type Measure"),
        vocabulary="eea.climateadapt.aceitems_key_type_measures_short",
        required=False,
    )


class FilteringForm(Form):  # form.SchemaForm):
    """Filtering form handling"""

    template = ViewPageTemplateFile("pt/filter_form.pt")

    label = ""
    description = ""

    prefix = ""
    ignoreContext = True
    method = "GET"

    fields = Fields(IFilteringSchema)
    css_class = "acecontent_filtering_tile"

    def __init__(self, context, request, *args, **kwargs):
        if "PARENT_REQUEST" in request:
            request = request["PARENT_REQUEST"]
        super(FilteringForm, self).__init__(context, request, *args, **kwargs)

    @ view.memoize
    def action(self):
        return self.context.absolute_url()


impacts_no_value = StaticWidgetAttribute(
    _("All climate impacts"), view=FilteringForm, field=IFilteringSchema["impact"]
)
sectors_no_value = StaticWidgetAttribute(
    _("All adaptation sectors"), view=FilteringForm, field=IFilteringSchema["sector"]
)
key_type_measures_no_value = StaticWidgetAttribute(
    _("All key type measures"), view=FilteringForm, field=IFilteringSchema["key_type_measure"]
)


# class FilterAceContentItemsTile(PersistentCoverTile, AceTileMixin, TranslationUtilsMixin):
#     implements(IFilterAceContentItemsTile)

#     short_name = "Filterable relevant AceContent"

#     is_configurable = True
#     is_editable = True
#     is_droppable = False
#     index = ViewPageTemplateFile("pt/filter_acecontent.pt")

#     @ property
#     def filterform(self):
#         form = FilteringForm(self.context, self.request)

#         form.update()

#         return form

#     def items(self):
#         kw, errors = self.filterform.extractData()
#         impact = kw["impact"]
#         sector = kw["sector"]
#         key_type_measure = kw["key_type_measure"]

#         count = self.data.get("nr_items", 5) or 5
#         query = self.build_query()

#         if impact:
#             query["climate_impacts"] = impact

#         if sector:
#             query["sectors"] = sector

#         if key_type_measure:
#             query["key_type_measures"] = key_type_measure
#         query["path"] = {"query": "/cca/{}".format(self.current_lang)}

#         res = self.catalog.searchResults(limit=count, **query)

#         return res[:count]

#     def view_more_url(self):
#         site = getSite()
#         base = site.absolute_url() + "/{}/data-and-downloads/?lang={}&"\
#             .format(self.current_lang, self.current_lang)

#         query = {
#             "elements": self.data.get("element_type"),
#             "search_type": self.data.get("search_type"),
#             "funding_programme": self.data.get("funding_programme") or "",
#             "SearchableText": self.data.get("search_text") or "",
#         }

#         kw, errors = self.filterform.extractData()
#         impact = kw["impact"]
#         sector = kw["sector"]
#         key_type_measure = kw["key_type_measure"]

#         if impact:
#             query["climate_impacts"] = impact

#         if sector:
#             query["sectors"] = sector

#         if key_type_measure:
#             query["key_type_measures"] = key_type_measure

#         return self.build_url(base, query, {})
