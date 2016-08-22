""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import _datatypes
from plone.directives import form
from urllib import urlencode
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.widget import StaticWidgetAttribute
from zope.component.hooks import getSite
from zope.interface import implements
from zope.schema import TextLine, Choice, List, Int, Bool

#from eea.climateadapt.vocabulary import aceitem_types

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
                            vocabulary="eea.climateadapt.special_tags_vocabulary"
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
                        #     'sectors': {'operator': 'or', 'query': [u'AGRICULTURE']}
                        if index in KEYWORD_INDEXES:
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

    def is_empty(self):
        return False

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
            result.append((_ace_types[search_type], len(brains), url, brains[:count]))

            return result

        # TODO: sync the links here to the index names and to the faceted indexes
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


class RelevantAceContentItemsTile(PersistentCoverTile, AceTileMixin):
    """ Relevant AceItem content
    """
    implements(IRelevantAceContentItemsTile)

    short_name = u'Relevant AceContent'

    is_configurable = True
    is_editable = True
    is_droppable = False

    index = ViewPageTemplateFile('pt/relevant_acecontent.pt')

    view_more = False

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

    def is_empty(self):
        return False

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []

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
        # return "%s/data-and-downloads?searchtext=%s&searchelements=%s&searchtypes=%s" % (
        #     site.absolute_url(), search_text, element_type, search_type
        # )

    def items(self):
        count = self.data.get('nr_items', 5) or 5
        query = self.build_query()
        res = self.catalog.searchResults(**query)

        if len(res) > count:
            self.view_more = True

        return res[:count]


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


class FilteringForm(Form):   #form.SchemaForm):
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
