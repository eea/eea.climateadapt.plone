""" A generic tile that can take applications
"""

from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class IEmbedAppTile(IPersistentCoverTile):

    embed = schema.Text(
        title=_(u'Embedding view'),
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


class EmbedAppTile(PersistentCoverTile):

    implements(IEmbedAppTile)

    index = ViewPageTemplateFile('pt/embedapp.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = u'Embed Application'

    def is_empty(self):
        return not (self.data.get('embed', None) or
                    self.data.get('title', None) or
                    self.data.get('description', None))

    def accepted_ct(self):
        """Return an empty list as no content types are accepted."""
        return []
