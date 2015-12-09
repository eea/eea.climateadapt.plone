""" A tile to implement the AST navigation
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IASTNavigationRoot
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


    def _get_ast_root(self):

        parent = self.context
        while True:
            if IASTNavigationRoot.providedBy(parent):
                break
            else:
                if hasattr(parent, 'aq_parent'):
                    parent = parent.aq_parent
                    if parent is None:
                        break
                else:
                    break

        if not IASTNavigationRoot.providedBy(parent):
            raise ValueError('No AST Root was found, mark '
                             'proper root with IASTNavigationRoot')
        return parent

    def get_nav_struct(self):
        ast_root = self._get_ast_root()
        res = []

        all_parts = ast_root.contentValues({'portal_type': 'Folder'})

        step = 0

        while True:
            for_this_step = [o.getId()
                             for o in all_parts
                             if o.getId().startswith('step-{0}'.format(step))]
            for_this_step.sort()
            if not for_this_step:
                break

            step += 1
            main = ast_root[for_this_step[0]]
            children = [(o['index_html'].Title(), o['index_html'].absolute_url())
                        for o in [ast_root[x] for x in for_this_step[1:]]]
            res.append((main['index_html'].Title(),
                        main['index_html'].absolute_url(), children))

        return res
