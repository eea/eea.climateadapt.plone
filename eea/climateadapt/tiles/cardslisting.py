""" Cards listing
"""

from collective.cover.tiles.base import (IPersistentCoverTile,
                                         PersistentCoverTile)
from zope import schema
from zope.interface import implements

from eea.climateadapt import MessageFactory as _
from plone.app.uuid.utils import uuidToObject
from plone.tiles.interfaces import ITileDataManager
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ICardsTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    uuid = schema.TextLine(
        title=_(u'UUID'),
        required=False,
        readonly=True,
    )


class CardsTile(PersistentCoverTile):
    """ Generic view tile
    """

    implements(ICardsTile)

    index = ViewPageTemplateFile('pt/cards.pt')

    is_configurable = True
    is_editable = True
    is_droppable = True
    short_name = u'Cards'

    def is_empty(self):
        return self.data.get('uuid', None) is None or \
            uuidToObject(self.data.get('uuid')) is None

    def get_context(self):
        uuid = self.data.get('uuid')
        if uuid:
            return uuidToObject(uuid)

    def sections(self):
        context = self.get_context()
        if not context:
            return []

        return context.getFolderContents(
            contentFilter={
                'sort_order': 'getObjPositionInParent',
                'portal_type': 'Folder'}
        )

    def accepted_ct(self):
        return ['Collection']

    def populate_with_object(self, obj):
        super(CardsTile, self).populate_with_object(
            obj)  # check permission

        if obj.portal_type in self.accepted_ct():

            data_mgr = ITileDataManager(self)
            data_mgr.set({'uuid': IUUID(obj)})
