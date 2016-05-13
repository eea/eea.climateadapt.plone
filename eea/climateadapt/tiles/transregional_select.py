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

    region = schema.Choice(
        title=_(u"Region"),
        vocabulary="eea.climateadapt.regions",
        required=True,
    )

regions = {
    'Adriatic-Ionian': [],
    'Alpine Space': [],
    'Northern Periphery and Arctic': [],
    'Atlantic Area': [],
    'Balkan-Mediterranean': [
        ('Bulgaria', '/countries/bulgaria'),
        ('Albania', ''),
    ],
    'Baltic Sea': [],
    'Central Europe': [],
    'Danube': [],
    'Mediterranean': [],
    'North Sea': [],
    'North West Europe': [
        ('Germany', '/countries/germany'),
    ],
    'South West Europe': [],
    'Other regions': [],
}

class TransRegionalSelectTile(PersistentCoverTile):
    """ TransRegionalSelect tile

    Shows a dropdown select for a region
    """

    implements(ITransRegionalSelectTile)

    index = ViewPageTemplateFile('pt/transregional_select.pt')

    is_configurable = False
    is_editable = True
    is_droppable = False
    short_name = u'Select trans region'

    def is_empty(self):
        return False

    def regions(self):
        site = getSite()

        catalog = getToolByName(site, 'portal_catalog')
        q = {
            "object_provides":
                "eea.climateadapt.interfaces.ITransnationalRegionMarker",
            'sort_on':'sortable_title'
        }
        brains = catalog.searchResults(**q)

        return [{'url': b.getURL(), 'title': b.Title} for b in brains]

    def countries(self):
        # a list of {'name': Country name, 'link': Country Link}
        region = self.data.get('region', None)
        if not region:
            return []
        return regions[region]
