""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
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
        required=True
    )


class SearchAceContentTile(PersistentCoverTile):
    """ Search Ace content tile
    """

    implements(ISearchAceContentTile)

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
