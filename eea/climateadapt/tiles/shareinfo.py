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


TYPES = {
    'DOCUMENT': ('eea.climateadapt.publicationreport', 'content'),
    'INFORMATIONSOURCE': ('eea.climateadapt.informationportal', 'content'),
    'GUIDANCE': ('eea.climateadapt.guidancedocument', 'content'),
    'TOOL': ('eea.climateadapt.tool', 'content'),
    'ORGANISATION': ('eea.climateadapt.organisation', 'content'),
    'INDICATOR': ('eea.climateadapt.indicator', 'content'),
    'MAPGRAPHDATASET': ('eea.climateadapt.mapgraphdataset', 'content'),

    'RESEARCHPROJECT': ('eea.climateadapt.aceproject', 'aceprojects'),
    'MEASURE': ('eea.climateadapt.adaptationoption', 'adaptationoption'),
    'ACTION': ('eea.climateadapt.casestudy', 'casestudy'),
}

#       'eea.climateadapt.aceproject': 'aceprojects'
#       'eea.climateadapt.adaptationoption': 'adaptationoption'
# 'eea.climateadapt.casestudy': 'casestudy'

DEFAULT_LOCATIONS = {
    'INDICATOR': 'content',
}


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
        factory, location = TYPES[type_]
        location = site.restrictedTraverse(location)
        return "{0}/++add++{1}".format(location.absolute_url(), factory)

    def link_title(self):
        type_ = self.data.get('shareinfo_type')
        label = dict(_cca_types)[type_]
        return u"Add a {0}".format(label)
