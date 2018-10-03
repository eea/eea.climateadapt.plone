""" A view that can be embeded in a tile.
It renders a search "portlet" for Ace content
"""

import logging
from urllib import urlencode

from collective.cover.interfaces import ICoverUIDsProvider
from collective.cover.tiles.base import (IPersistentCoverTile,
                                         PersistentCoverTile)
from collective.cover.tiles.list import IListTile
from zope.component.hooks import getSite
from zope.interface import implements
from zope.schema import Bool, Choice, Dict, Int, List, TextLine

from AccessControl import Unauthorized
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import _datatypes
from plone import api
from plone.api import portal
from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.memoize import view
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.widget import StaticWidgetAttribute

logger = logging.getLogger('eea.climateadapt')


class ISearchAceContentTile(IPersistentCoverTile):

    title = TextLine(
        title=_(u'Title'),
        required=False,
    )

    search_text = TextLine(
        title=_(u'Search Text'),
        required=False,
        default=u"",
    )

    search_type = List(
        title=_(u"Aceitem type"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.search_types_vocabulary",
        )
    )

    element_type = List(
        title=_(u"Element type"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.element_types_vocabulary",
        )
    )

    sector = List(
        title=_(u"Sector"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        )
    )

    special_tags = List(title=_(u"Special tags"),
                        required=False,
                        value_type=Choice(
                            vocabulary="eea.climateadapt.special_tags"
                        )
                        )

    countries = List(title=_(u"Countries"),
                     required=False,
                     value_type=Choice(
                         vocabulary="eea.climateadapt.ace_countries"
                     )
                     )

    nr_items = Int(
        title=_(u"Nr of items to show"),
        required=True,
        default=5,
    )


KEYWORD_INDEXES = ['search_type', 'elements', 'sectors']


class AceTileMixin(object):
    """ Mixin class for ace search/relevant content tiles
    """

    @property
    def catalog(self):
        catalog = getToolByName(self.context, 'portal_catalog')

        return catalog

    def build_query(self):

        query = {
            'review_state': 'published'
        }

        # todo: do countries
        # map of {tile field: index name}
        map = {
            'search_type': 'search_type',
            'element_type': 'elements',
            'search_text': 'SearchableText',
            'special_tags': 'special_tags',
            'sector': 'sectors',
        }

        sort_map = {
            'RATING': 'rating',
            'NAME': 'sortable_title',
        }

        sort = self.data.get('sortBy')

        if sort:
            query['sort_on'] = sort_map[sort]
            query['sort_order'] = 'reverse'

        for setting_name, index_name in map.items():
            setting = self.data.get(setting_name, '')

            if setting:
                if index_name in KEYWORD_INDEXES:   # and len(setting) > 1:
                    query[index_name] = {'query': setting, 'operator': 'or'}
                else:
                    query[index_name] = setting

        # get rid of special_tags index, just use the SearchableText
        # the special_tags field is indexed into the SearchableText
        st = self.data.get('special_tags')


        if st:
            query.pop('special_tags', None)

            if isinstance(st, basestring):
                st = st.split(u' ')
            words = query.pop('SearchableText', u'').split(u' ')
            query['SearchableText'] = u' '.join(set(words + st))

        return query

    def build_url(self, url, query, kw):
        q = query.copy()
        q.update(kw)
        x = {}
        searchtype = q.pop('search_type', None)

        if searchtype:
            q['searchtype'] = searchtype

        for index, v in q.items():
            if v:
                if index not in ['sort_on', 'sort_order']:
                    if isinstance(v, (tuple, list)):
                        x[index] = v
                    else:
                        # keyword indexes appear ex:
                        #  'sectors': {'operator': 'or',
                        #  'query': [u'AGRICULTURE']}

                        if index in KEYWORD_INDEXES:
                            if isinstance(v, str):
                                x[index] = v
                            else:
                                x[index] = v['query']
                        else:
                            x[index] = v

        return url + "#" + urlencode(x, True)


class SearchAceContentTile(PersistentCoverTile, AceTileMixin):
    """ Search Ace content tile
    It shows links to the search page, for all aceitems_types.
    """

    implements(ISearchAceContentTile)

    # available options:
    # title
    # search_text
    # element_type
    # sector
    # special_tags
    # countries

    index = ViewPageTemplateFile('pt/search_acecontent.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = u'Search AceContent'

    @view.memoize
    def is_empty(self):
        return False

    @view.memoize
    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""

        return []

    def sections(self):
        """ Returns a list of (section name, section count, section_url)
        """
        site = getSite()
        base = site.absolute_url() + "/data-and-downloads?"

        result = []

        _ace_types = dict(_datatypes)

        search_type = self.data.get('search_type')

        if search_type and len(search_type) == 1:
            # Special case when we want to show the results, like RelevantTile
            search_type = search_type[0]
            query = self.build_query()
            count = self.data.get('nr_items', 5)
            brains = self.catalog.searchResults(**query)
            url = self.build_url(base, query, {})
            result.append((_ace_types[search_type],
                           len(brains), url, brains[:count]))

            return result

        # TODO: sync the links here to the index names and to the faceted
        # indexes
        query = self.build_query()

        element_type = self.data.pop('element_type', [])

        for typeid, typelabel in _datatypes:
            if search_type:
                if not (typeid in search_type):
                    continue
            q = query.copy()

            q.update({'search_type': typeid})

            if element_type:
                q.update({'elements': element_type})

            count = len(self.catalog.searchResults(**q))

            if count:
                result.append((
                    typelabel,
                    count,
                    self.build_url(base, q, {}),
                ))

        return result


class IRelevantAceContentItemsTile(ISearchAceContentTile):

    show_share_btn = Bool(
        title=_(u"Show the share button"),
        default=False,
    )

    uuids = Dict(
        title=_(u'Elements'),
        key_type=TextLine(),
        value_type=Dict(
            key_type=TextLine(),
            value_type=TextLine(),
        ),
        required=False,
    )

    form.omitted('uuids')


class RelevantAceContentItemsTile(PersistentCoverTile, AceTileMixin):
    """ Relevant AceItem content
    """
    implements(IRelevantAceContentItemsTile, IListTile)

    short_name = u'Relevant AceContent'

    is_configurable = True
    is_editable = True
    is_droppable = True

    index = ViewPageTemplateFile('pt/relevant_acecontent.pt')

    view_more = False

    @property
    def is_available(self):
        return bool(self.items())

    def show_share_btn(self):
        search_type = self.data.get('search_type')

        if search_type in ['DOCUMENT', 'INFORMATIONSOURCE',
                           'GUIDANCE', 'TOOL', 'REASEARCHPROJECT',
                           'MEASURE', 'ORGANISATION']:

            return True

        # <c:if test="${aceitemtype eq 'DOCUMENT' || aceitemtype eq
        # 'INFORMATIONSOURCE' || aceitemtype eq 'GUIDANCE' ||
        # aceitemtype eq 'TOOL' || aceitemtype eq
        # 'RESEARCHPROJECT' || aceitemtype eq 'MEASURE' ||
        # aceitemtype eq 'ORGANISATION'}" >

    @view.memoize
    def is_empty(self):
        return False

    @view.memoize
    def accepted_ct(self):
        """ Return accepted drag/drop content types for this tile.
        """

        return ['Document', 'Folder', 'collective.cover.content']

    def view_more_url(self):
        site = getSite()
        base = site.absolute_url() + "/data-and-downloads?"

        q = {
            'elements': self.data.get('element_type'),
            'search_type': self.data.get('search_type'),
            'SearchableText': self.data.get('search_text') or ""
        }

        return self.build_url(base, q, {})

        # "http://climate-adapt.eea.europa.eu/data-and-downloads?searchtext=obs-scen-gen&searchelements=OBSERVATIONS&searchtypes=DOCUMENT"
        # return
        # "%s/data-and-downloads?searchtext=%s&searchelements=%s&searchtypes=%s"
        # % ( site.absolute_url(), search_text, element_type, search_type)

    @view.memoize
    def icon_images(self):
        root = portal.get()

        if 'tile_icons' not in root.objectIds():
            return []

        tile_icons = root['tile_icons']

        return tile_icons.objectValues()

    def get_icons(self, brain):
        special_tags = brain.special_tags or []
        images = self.icon_images()
        icons = [image for image in images if image.getId() in special_tags]

        return icons

    @view.memoize
    def items(self):
        count = self.data.get('nr_items', 5) or 5
        query = self.build_query()
        res = self.catalog.searchResults(**query)

        if len(res) > count:
            self.view_more = True

        items = res[:count]

        return items

    @view.memoize
    def assigned(self):
        """Return the list of objects stored in the tile as UUID. If an UUID
        has no object associated with it, removes the UUID from the list.
        :returns: a list of objects.
        """
        # self.set_limit()

        # always get the latest data
        uuids = ITileDataManager(self).get().get('uuids', None)

        results = list()

        if uuids:
            ordered_uuids = [(k, v) for k, v in uuids.items()]
            ordered_uuids.sort(key=lambda x: x[1]['order'])

            for uuid in [i[0] for i in ordered_uuids]:
                obj = uuidToObject(uuid)

                if obj:
                    results.append(obj)

                else:
                    # maybe the user has no permission to access the object
                    # so we try to get it bypassing the restrictions
                    catalog = api.portal.get_tool('portal_catalog')
                    brain = catalog.unrestrictedSearchResults(UID=uuid)

                    if not brain:
                        # the object was deleted; remove it from the tile
                        self.remove_item(uuid)
                        logger.debug(
                            'Nonexistent object {0} removed from '
                            'tile'.format(uuid)
                        )

        return results

    def populate_with_object(self, obj):
        """ Add an object to the list of items
        :param obj: [required] The object to be added
        :type obj: Content object
        """
        super(RelevantAceContentItemsTile, self).populate_with_object(obj)
        # check permission
        uuids = ICoverUIDsProvider(obj).getUIDs()

        if uuids:
            self.populate_with_uuids(uuids)

    def populate_with_uuids(self, uuids):
        """ Add a list of elements to the list of items. This method will
        append new elements to the already existing list of items
        :param uuids: The list of objects' UUIDs to be used
        :type uuids: List of strings
        """

        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to add content to this tile'))
        # self.set_limit()
        data_mgr = ITileDataManager(self)

        old_data = data_mgr.get()

        if old_data['uuids'] is None:
            # If there is no content yet, just assign an empty dict
            old_data['uuids'] = dict()

        uuids_dict = old_data.get('uuids')

        if not isinstance(uuids_dict, dict):
            # Make sure this is a dict
            uuids_dict = old_data['uuids'] = dict()

        # if uuids_dict and len(uuids_dict) > self.limit:
        #     # Do not allow adding more objects than the defined limit
        #     return

        order_list = [int(val.get('order', 0))
                      for key, val in uuids_dict.items()]

        if len(order_list) == 0:
            # First entry
            order = 0
        else:
            # Get last order position and increment 1
            order_list.sort()
            order = order_list.pop() + 1

        for uuid in uuids:
            if uuid not in uuids_dict.keys():
                entry = dict()
                entry[u'order'] = unicode(order)
                uuids_dict[uuid] = entry
                order += 1

        old_data['uuids'] = uuids_dict
        data_mgr.set(old_data)

    def replace_with_uuids(self, uuids):
        """ Replaces the whole list of items with a new list of items
        :param uuids: The list of objects' UUIDs to be used
        :type uuids: List of strings
        """

        if not self.isAllowedToEdit():
            raise Unauthorized(
                _('You are not allowed to add content to this tile'))
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        # Clean old data
        old_data['uuids'] = dict()
        data_mgr.set(old_data)
        # Repopulate with clean list
        self.populate_with_uuids(uuids)

    @view.memoize
    def get_uuid(self, obj):
        """Return the UUID of the object.
        :param obj: [required]
        :type obj: content object
        :returns: the object's UUID
        """

        return IUUID(obj, None)

    def remove_item(self, uuid):
        """ Removes an item from the list
        :param uuid: [required] uuid for the object that wants to be removed
        :type uuid: string
        """
        super(RelevantAceContentItemsTile, self).remove_item(uuid)
        # check permission
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        uuids = data_mgr.get()['uuids']

        if uuid in uuids.keys():
            del uuids[uuid]
        old_data['uuids'] = uuids
        data_mgr.set(old_data)


class IFilterAceContentItemsTile(IRelevantAceContentItemsTile):
    """ Schema for filter aceitems
    This is a results listing, but with two dropdowns to filter:
    * climate impact
    * adaptation sector
    """


class IFilteringSchema(form.Schema):
    impact = Choice(
        title=_(u"Climate impact"),
        vocabulary="eea.climateadapt.aceitems_climateimpacts",
        required=False
    )

    sector = Choice(
        title=_(u"Sector"),
        vocabulary="eea.climateadapt.aceitems_sectors",
        required=False
    )


class FilteringForm(Form):   # form.SchemaForm):
    """ Filtering form handling
    """

    template = ViewPageTemplateFile('pt/filter_form.pt')

    label = u""
    description = u""

    prefix = ''
    ignoreContext = True
    method = "GET"

    fields = Fields(IFilteringSchema)
    css_class = "acecontent_filtering_tile"

    def __init__(self, context, request, *args, **kwargs):
        if 'PARENT_REQUEST' in request:
            request = request['PARENT_REQUEST']
        super(FilteringForm, self).__init__(context, request, *args, **kwargs)

    @view.memoize
    def action(self):
        return self.context.absolute_url()


impacts_no_value = StaticWidgetAttribute(u"All climate impacts",
                                         view=FilteringForm,
                                         field=IFilteringSchema['impact'])
sectors_no_value = StaticWidgetAttribute(u"All adaptation sectors",
                                         view=FilteringForm,
                                         field=IFilteringSchema['sector'])


class FilterAceContentItemsTile(PersistentCoverTile, AceTileMixin):
    implements(IFilterAceContentItemsTile)

    short_name = u'Filterable relevant AceContent'

    is_configurable = True
    is_editable = True
    is_droppable = False
    index = ViewPageTemplateFile('pt/filter_acecontent.pt')

    @property
    def filterform(self):
        form = FilteringForm(self.context, self.request)

        form.update()

        return form

    def items(self):
        kw, errors = self.filterform.extractData()
        impact = kw['impact']
        sector = kw['sector']

        count = self.data.get('nr_items', 5) or 5
        query = self.build_query()

        if impact:
            query['climate_impacts'] = impact

        if sector:
            query['sectors'] = sector

        res = self.catalog.searchResults(limit=count, **query)

        return res[:count]

    def view_more_url(self):
        site = getSite()
        base = site.absolute_url() + "/data-and-downloads?"

        query = {
            'elements': self.data.get('element_type'),
            'search_type': self.data.get('search_type'),
            'SearchableText': self.data.get('search_text') or ""
        }

        kw, errors = self.filterform.extractData()
        impact = kw['impact']
        sector = kw['sector']

        if impact:
            query['climateimpacts'] = impact

        if sector:
            query['sectors'] = sector

        return self.build_url(base, query, {})
