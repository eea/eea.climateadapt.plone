""" A tile to implement the AST navigation
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.interface import implements


class IASTNavigationTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class ASTNavigationTile(PersistentCoverTile):
    """ AST Navigation tile

    Shows the navigation tile
    """

    implements(IASTNavigationTile)

    index = ViewPageTemplateFile('pt/ast_navigation.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = u'AST Navigation'

    def is_empty(self):
        return False


class IUrbanASTNavigationTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class UrbanASTNavigationTile(PersistentCoverTile):
    """ AST Navigation tile

    Shows the navigation tile
    """

    implements(IASTNavigationTile)

    index = ViewPageTemplateFile('pt/urbanast_navigation.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = u'AST Navigation'

    def is_empty(self):
        return False

    # def _get_ast_root(self):
    #
    #     parent = self.context
    #     while True:
    #         if IASTNavigationRoot.providedBy(parent):
    #             break
    #         else:
    #             if hasattr(parent, 'aq_parent'):
    #                 parent = parent.aq_parent
    #                 if parent is None:
    #                     break
    #             else:
    #                 break
    #
    #     if not IASTNavigationRoot.providedBy(parent):
    #         raise ValueError('No AST Root was found, mark '
    #                          'proper root with IASTNavigationRoot')
    #     return parent
    #
    #
    # def _title(self, obj):
    #     obj = obj.aq_self
    #     title = getattr(obj, "_ast_title", obj.Title())
    #     return title
    #
    # def get_nav_struct(self):
    #     ast_root = self._get_ast_root()
    #     res = []
    #
    #     all_parts = ast_root.contentValues({'portal_type': 'Folder'})
    #
    #     step = 0
    #
    #     T = self._title
    #
    #     while step < len(all_parts):
    #         for_this_step = [o.getId()
    #                          for o in all_parts
    #                          if o.getId().startswith('step-{0}'.format(step))]
    #         for_this_step.sort()
    #         step += 1
    #
    #         if not for_this_step:
    #             continue
    #
    #         main = ast_root[for_this_step[0]]
    #         children = [(o['index_html'].Title(), o['index_html'].absolute_url())
    #                     for o in [ast_root[x] for x in for_this_step[1:]]]
    #         res.append((step,
    #                     #main['index_html'].Title(),
    #                     T(main['index_html']),
    #                     main['index_html'].absolute_url(),
    #                     children))
    #
    #
    #     # process extra documents that have weird ids
    #     for folder in all_parts:
    #         if not folder.getId().startswith('step'):
    #             cover = folder['index_html']
    #             step = getattr(cover, '_ast_navigation_step', 0)
    #             info = (T(cover), cover.absolute_url())
    #             # try to find the proper index position
    #             for branch in res:
    #                 if branch[0] == step:
    #                     branch[3].append(info)
    #
    #     return res


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


class IASTHeaderTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    step = schema.Int(
        title=_(u"AST Step"),
        required=True,
        default=1,
    )


class ASTHeaderTile(PersistentCoverTile):
    """ AST Header tile
    """

    implements(IASTHeaderTile)

    index = ViewPageTemplateFile('pt/ast_header.pt')

    is_configurable = False
    is_editable = True
    is_droppable = False
    short_name = u'AST Header'

    def is_empty(self):
        return False
