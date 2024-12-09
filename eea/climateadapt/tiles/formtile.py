""" A view that can be embeded in a tile.

It renders an easyform "portlet"
"""

# from collective.cover.tiles.base import IPersistentCoverTile
# from collective.cover.tiles.base import PersistentCoverTile
# from zope import schema
# from zope.interface import implements
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
# from plone.app.uuid.utils import uuidToObject
# from zope.component import getMultiAdapter
# from zope.component.interfaces import ComponentLookupError


# class IFormTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=False,
#     )

#     form_uuid = schema.TextLine(
#         title='Form UUID',
#         required=True
#     )


# class FormTile(PersistentCoverTile):
#     """
#     """

#     implements(IFormTile)

#     is_configurable = True
#     is_editable = True
#     is_droppable = True
#     index = ViewPageTemplateFile('pt/form_tile.pt')

#     def getFormEmbeddedView(self):
#         uuid = self.data.get('form_uuid')
#         if not uuid:
#             return ''
#         obj = uuidToObject(uuid)
#         if not obj:
#             return ''
#         try:
#             embedded_view = getMultiAdapter((obj, self.request), name="embedded")
#         except ComponentLookupError as e:
#             print(e)
#             return ''
#         return embedded_view
