""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import aceitem_types
from plone.directives import form
from urllib import urlencode
from z3c.form.field import Fields
from z3c.form.form import Form
from zope.component.hooks import getSite
from zope.interface import implements
from zope.schema import TextLine, Choice, List, Int, Bool


# TODO: use an adaptor for the choice widgets to set the noValueMessage


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

        keyword_indexes = ['search_type', 'element_type', 'special_tags',
                           'sectors']

        # todo: do countries
        map = {
            'search_type': 'search_type',        # importeddata: plone field
            'element_type': 'element_type',
            'search_text': 'SearchableText',
            'special_tags': 'special_tags',
            'sector': 'sectors',
        }

        sort_map = {
            'RATING': 'rating',                     # importeddata: plone field
            'NAME': 'sortable_title',
        }

        sort = self.data.get('sortBy')
        if sort:
            query['sort_on'] = sort_map[sort]
            query['sort_order'] = 'reverse'

        for setting_name, index_name in map.items():
            setting = self.data.get(setting_name, '')
            if setting:
                if index_name not in keyword_indexes:
                    query[index_name] = setting
                else:
                    query[index_name] = {'query': setting, 'operator': 'or'}

        # is this needed?
        # for k, v in query.items():
        #     if v is None:
        #         del query[k]

        # get rid of special_tags index, just use the SearchableText
        # the special_tags field is indexed into the SearchableText
        st = query.pop('special_tags', '')
        if st:
            text = query.pop('SearchableText', '') + ' ' + st
            query['SearchableText'] = text

        return query

    def build_url(self, url, query, kw):
        q = query.copy()
        q.update(kw)
        x = {}
        searchtype = q.pop('search_type', None)
        if searchtype:
            q['searchtype'] = searchtype
        for k, v in q.items():
            if v:
                if k not in ['sort_on', 'sort_order']:
                    if isinstance(v, (tuple, list)):
                        x[k] = v[0]
                    else:
                        x[k] = v
        return url + "#" + urlencode(x)


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

        # TODO: sync the links here to the index names and to the faceted indexes
        query = self.build_query()

        element_type = self.data.get('element_type')

        for info in aceitem_types:
            q = query.copy()
            q.update({'search_type': info.id})
            count = len(self.catalog.searchResults(**q))
            if count:
                result.append((
                    info.label,
                    count,
                    self.build_url(base, q, {'elements':element_type}),
                ))

        return result


class IRelevantAceContentItemsTile(ISearchAceContentTile):

    search_type = List(
        title=_(u"Aceitem type"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.search_types_vocabulary",
        )
    )

    nr_items = Int(
        title=_(u"Nr of items to show"),
        required=True,
        default=5,
    )

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
        res = self.catalog.searchResults(limit=count, **query)

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

    # sector = List(
    #     title=_(u"Sector"),
    #     required=False,
    #     value_type=Choice(
    #         vocabulary="eea.climateadapt.aceitems_sectors",
    #     )
    # )


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

        kw, errors = self.filterform.extractData()
        impact = kw['impact']
        sector = kw['sector']

        query = {
            'elements': self.data.get('element_type'),
            'search_type': self.data.get('search_type'),
            'SearchableText': self.data.get('search_text') or ""
        }

        if impact:
            query['climate_impacts'] = impact
        if sector:
            query['sectors'] = sector

        return self.build_url(base, query, {})
