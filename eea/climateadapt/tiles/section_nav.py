""" Subsection navigation
"""

# from collective.cover.tiles.base import (IPersistentCoverTile,
                                        #  PersistentCoverTile)
# from zope import schema
# from zope.interface import implements

# from plone.app.uuid.utils import uuidToObject
# from plone.tiles.interfaces import ITileDataManager
# from plone.uuid.interfaces import IUUID
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


# class ISectionNavTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=True,
#     )

#     uuid = schema.TextLine(
#         title='UUID',
#         required=False,
#         readonly=True,
#     )


# class SectionNavTile(PersistentCoverTile):
#     """ Generic view tile
#     """

#     implements(ISectionNavTile)

#     index = ViewPageTemplateFile('pt/section_nav.pt')

#     is_configurable = True
#     is_editable = True
#     is_droppable = True
#     short_name = 'Section Navigation'

#     def is_empty(self):
#         return self.data.get('uuid', None) is None or \
#             uuidToObject(self.data.get('uuid')) is None

#     def get_context(self):
#         uuid = self.data.get('uuid')
#         if uuid:
#             return uuidToObject(uuid)

#     def sections(self):
#         context = self.get_context()
#         if not context:
#             return []

#         return context.getFolderContents(
#             contentFilter={
#                 'sort_order': 'getObjPositionInParent',
#                 'portal_type': 'Folder'}
#         )

#     def accepted_ct(self):
#         return ['Folder']

#     def populate_with_object(self, obj):
#         super(SectionNavTile, self).populate_with_object(
#             obj)  # check permission

#         if obj.portal_type in self.accepted_ct():

#             data_mgr = ITileDataManager(self)
#             data_mgr.set({'uuid': IUUID(obj)})
