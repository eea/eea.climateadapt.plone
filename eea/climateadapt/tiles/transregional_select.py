""" A tile to implement the transregional select dropdown
"""

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from zope import schema
from zope.component.hooks import getSite
from zope.interface import implements


class ITransRegionalSelectTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class TransRegionalSelectTile(PersistentCoverTile):
    """ TransRegionalSelect tile

    Shows a dropdown select for a region
    """

    implements(ITransRegionalSelectTile)

    index = ViewPageTemplateFile('pt/transregional_select.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = u'Select trans region'

    def is_empty(self):
        return False

    def regions(self):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')

        brains = catalog.searchResults(
            object_provides=
            "eea.climateadapt.interfaces.ITransnationalRegionMarker")

        return [{'url': b.getURL(), 'title': b.Title} for b in brains]
