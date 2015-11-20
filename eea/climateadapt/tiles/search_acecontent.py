""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import aceitem_types
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements


class ISearchAceContentTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    search_text = schema.TextLine(
        title=_(u'Search Text'),
        required=False,
        default=u"",
    )

    element_type = schema.Choice(
        title=_(u"Element type"),
        vocabulary="eea.climateadapt.element_types_vocabulary",
        required=False
    )

    sector = schema.Choice(
        title=_(u"Sector"),
        vocabulary="eea.climateadapt.aceitems_sectors",
        required=False
    )

    special_tags = schema.List(title=_(u"Special tags"),
                               required=False,
                               value_type=schema.Choice(
                                   vocabulary="eea.climateadapt.special_tags_vocabulary"
                               )
                               )

    countries = schema.List(title=_(u"Countries"),
                            required=False,
                            value_type=schema.Choice(
                                vocabulary="eea.climateadapt.ace_countries"
                            )
                            )


class SearchAceContentTile(PersistentCoverTile):
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
        catalog = getToolByName(self.context, 'portal_catalog')
        result = []
        url = site.absolute_url() + "/data-and-downloads?searchtext=&searchelements=%s&searchtypes=%s"
#       "http://adapt-test.eea.europa.eu/data-and-downloads?"
#       "searchtext=&searchelements=OBSERVATIONS&searchtypes=ORGANISATION"
        element_type = self.data.get('element_type')
        for info in aceitem_types:
            res = catalog.searchResults(search_type=info.id)
            result.append((
                info.label,
                len(res),
                url % (element_type, info.id),
            ))

        return result


class IRelevantAceContentItemsTile(ISearchAceContentTile):

    search_type = schema.Choice(
        title=_(u"Aceitem type"),
        vocabulary="eea.climateadapt.search_types_vocabulary",
        required=True
    )

    nr_items = schema.Int(
        title=_(u"Nr of items to show"),
        required=True,
        default=5,
    )

    show_share_btn = schema.Bool(
        title=_(u"Show the share button"),
        default=False,
    )


class RelevantAceContentItemsTile(PersistentCoverTile):
    """ Relevant AceItem content
    """
    implements(IRelevantAceContentItemsTile)

    short_name = u'Relevant AceContent'

    is_configurable = True
    is_editable = True
    is_droppable = False

    index = ViewPageTemplateFile('pt/relevant_acecontent.pt')

    view_more = False

    def is_empty(self):
        return False

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []

    def view_more_url(self):
        site = getSite()
        element_type = self.data.get('element_type')
        search_type = self.data.get('search_type')
        search_text = self.data.get('search_text') or ""
        # "http://climate-adapt.eea.europa.eu/data-and-downloads?searchtext=obs-scen-gen&searchelements=OBSERVATIONS&searchtypes=DOCUMENT"
        return "%s/data-and-downloads?searchtext=%s&searchelements=%s&searchtypes=%s" % (
            site.absolute_url(), search_text, element_type, search_type
        )

    def items(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        count = self.data.get('nr_items', 5) or 5

        query = {}
        # todo: do countries
        map = {'search_type': 'search_type',        # importeddata: plone field
               'element_type': 'element_type',
               'search_text': 'SearchableText',
               'special_tags': 'special_tags',
               }

        sort_map = {
            'RATING': 'rating',                     # importeddata: plone field

        }

        sort = self.data.get('sortOn')
        if sort:
            query['sort_on'] = sort_map[sort]
            query['sort_order'] = 'reverse'

        for k, v in map.items():
            p = self.data.get(k, '')
            if p:
                query[v] = p

        res = catalog.searchResults(limit=count, **query)
        if len(res) > count:
            self.view_more = True
        return res[:count]
