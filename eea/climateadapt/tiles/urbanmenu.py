""" A tile to implement the urban menu
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.interface import implements


class IUrbanMenuTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class UrbanMenuTile(PersistentCoverTile):
    """ Urban Menu tile
    """

    implements(IUrbanMenuTile)

    index = ViewPageTemplateFile('pt/urbanmenu.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = u'Urban Menu'

    def is_empty(self):
        return False
