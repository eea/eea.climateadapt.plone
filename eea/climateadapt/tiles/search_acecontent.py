""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class ISearchAceContentTile(IPersistentCoverTile):

    params = schema.Text(
        title=_(u'Params'),
        required=False,
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
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
        return not (self.data.get('params', None) or
                    self.data.get('title', None) or
                    self.data.get('description', None))

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
