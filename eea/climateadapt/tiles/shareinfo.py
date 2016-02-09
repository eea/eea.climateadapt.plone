""" A view that can be embeded in a tile.

It renders a search "portlet" for Ace content
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import _cca_types
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements

class IShareInfoTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )

    shareinfo_type = schema.Choice(
        title=_(u"Share info type"),
        vocabulary="eea.climateadapt.cca_types",
        required=False
    )


class ShareInfoTile(PersistentCoverTile):
    """ Share info tile

    It shows a button with link to creating content of a certain type
    """

    implements(IShareInfoTile)

    index = ViewPageTemplateFile('pt/shareinfo.pt')

    is_configurable = True
    is_editable = True
    is_droppable = False
    short_name = u'Share info'

    def is_empty(self):
        return False

    def link_url(self):
        site = getSite()    # TODO: fix this link
        type_ = self.data.get('shareinfo_type')
        return "{0}/create?type_name={1}".format(site.absolute_url(), type_)

    def link_title(self):
        type_ = self.data.get('shareinfo_type')
        label = dict(_cca_types)[type_]
        return u"Add a {0}".format(label)
