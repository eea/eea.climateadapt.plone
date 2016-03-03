""" A view that can be embeded in a tile.

It renders an easyform "portlet"
"""

from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.uuid.utils import uuidToObject
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError


class IFormTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    form_uuid = schema.TextLine(
        title=_(u'Form UUID'),
        required=True
    )


class FormTile(PersistentCoverTile):
    """ Search Ace content tile

    It shows links to the search page, for all aceitems_types.
    """

    implements(IFormTile)

    is_configurable = True
    is_editable = True
    is_droppable = True
    index = ViewPageTemplateFile('pt/form_tile.pt')

    def getFormEmbeddedView(self):
        uuid = self.data.get('form_uuid')
        if not uuid:
            return ''
        site = getSite()
        obj = uuidToObject(site.test.UID())
        if not obj:
            return ''
        try:
            embedded_view = getMultiAdapter((obj, self.request), name="embedded")
        except ComponentLookupError as e:
            print e
            return ''
        return embedded_view
