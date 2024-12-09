""" A tile to implement the AST navigation
"""

# from collective.cover.tiles.base import (IPersistentCoverTile,
#                                          PersistentCoverTile)
# from zope import schema
# from zope.interface import implements

# from eea.climateadapt.interfaces import IASTNavigationRoot
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


# class IASTNavigationTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=False,
#     )


# def active_tab(context, iface):
#     request = context.REQUEST

#     for parent in request.PARENTS:
#         if not iface.providedBy(parent):
#             context = parent
#         else:
#             break

#     try:
#         id = context.getId()

#         if 'step-' not in id:
#             return 0

#         id = id.replace('step-', '')
#         bits = id.split('-', 1)

#         return int(bits[0])
#     except:
#         return 0


# class ASTNavigationTile(PersistentCoverTile):
#     """ AST Navigation tile

#     Shows the navigation tile
#     """

#     implements(IASTNavigationTile)

#     index = ViewPageTemplateFile('pt/ast_navigation.pt')

#     is_configurable = False
#     is_editable = False
#     is_droppable = False
#     short_name = 'AST Navigation'

#     def is_empty(self):
#         return False

#     def active_tab(self):
#         return active_tab(self.context, IASTNavigationRoot)


# class IUrbanASTNavigationTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=False,
#     )


# class UrbanASTNavigationTile(PersistentCoverTile):
#     """ AST Navigation tile

#     Shows the navigation tile
#     """

#     implements(IASTNavigationTile)

#     index = ViewPageTemplateFile('pt/urbanast_navigation.pt')

#     is_configurable = False
#     is_editable = False
#     is_droppable = False
#     short_name = 'AST Navigation'

#     def is_empty(self):
#         return False

#     def active_tab(self):
#         return active_tab(self.context, IASTNavigationRoot)


# class IUrbanMenuTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=False,
#     )


# class UrbanMenuTile(PersistentCoverTile):
#     """ Urban Menu tile
#     """

#     implements(IUrbanMenuTile)

#     index = ViewPageTemplateFile('pt/urbanmenu.pt')

#     is_configurable = False
#     is_editable = False
#     is_droppable = False
#     short_name = 'Urban Menu'

#     def is_empty(self):
#         return False


# class IASTHeaderTile(IPersistentCoverTile):

#     title = schema.TextLine(
#         title='Title',
#         required=False,
#     )

#     step = schema.Int(
#         title="AST Step",
#         required=True,
#         default=1,
#     )


# class ASTHeaderTile(PersistentCoverTile):
    # """ AST Header tile
    # """

    # implements(IASTHeaderTile)

    # index = ViewPageTemplateFile('pt/ast_header.pt')

    # is_configurable = False
    # is_editable = True
    # is_droppable = False
    # short_name = 'AST Header'

    # def is_empty(self):
    #     return False
