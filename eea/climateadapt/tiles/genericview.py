""" Generic view tile, uses a view name to render content
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from zope import schema
from zope.component import queryMultiAdapter
from zope.interface import implements


class IGenericViewTile(IPersistentCoverTile):

    title = schema.TextLine(
        title='Title',
        required=True,
    )

    view_name = schema.TextLine(
        title='View name',
        required=True,
    )


class GenericViewTile(PersistentCoverTile):
    """ Generic view tile
    """

    implements(IGenericViewTile)

    index = ViewPageTemplateFile('pt/genericview.pt')

    is_configurable = False
    is_editable = True
    is_droppable = False
    short_name = 'Generic View'

    def is_empty(self):
        return False

    def render_inner_view(self):
        view_name = self.data.get('view_name')
        if view_name:
            view = queryMultiAdapter((self.context, self.request), name=view_name)
            if view:
                return view()
            else:
                return "View not found: %s" % view_name
        return ""
