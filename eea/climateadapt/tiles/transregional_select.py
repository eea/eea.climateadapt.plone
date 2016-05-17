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
    'Adriatic-Ionian': [
        ('Croatia', '/countries/croatia'),
        ('Greece', '/countries/greece'),
        ('Italy', '/countries/italy'),
        ('Slovenia', '/countries/slovenia'),
        ('Albania', ''),
        ('Bosnia and Herzegovina', ''),
        ('Montenegro', ''),
        ('Serbia', ''),
    ],
    'Alpine Space': [
        ('Austria', '/countries/austria'),
        ('France', '/countries/france'),
        ('Germany', '/countries/germany'),
        ('Italy', '/countries/italy'),
        ('Slovenia', '/countries/slovenia'),
        ('Liechtenstein', ''),
        ('Switzerland', '/countries/switzerland'),
    ],
    'Northern Periphery and Arctic': [
        ('Finland', '/countries/finland'),
        ('Ireland', '/countries/ireland'),
        ('Sweden', '/countries/sweden'),
        ('United Kingdom', '/countries/united-kingdom'),
        ('Iceland', '/countries/iceland'),
        ('Norway', '/countries/norway'),
        ('Greenland', ''),
        ('Faroe Islands', ''),
    ],
    'Atlantic': [
        ('France', '/countries/france'),
        ('Ireland', '/countries/ireland'),
        ('Portugal', '/countries/portugal'),
        ('Spain', '/countries/spain'),
        ('United Kingdom', '/countries/united-kingdom'),
    ],
    'Balkan-Mediterranean': [
        ('Bulgaria', '/countries/bulgaria'),
        ('Cyprus', '/countries/cyprus'),
        ('Greece', '/countries/greece'),
        ('Albania', ''),
        ('former Yugoslav Republic of Macedonia', ''),
    ],
    'Baltic Sea': [
        ('Denmark', '/countries/denmark'),
        ('Estonia', '/countries/estonia'),
        ('Finland', '/countries/finland'),
        ('Germany', '/countries/germany'),
        ('Latvia', '/countries/latvia'),
        ('Lithuania', '/countries/lithuania'),
        ('Poland', '/countries/poland'),
        ('Sweden', '/countries/sweden'),
        ('Norway', '/countries/norway'),
        ('Russia', ''),
        ('Belarus', ''),
    ],
    'Central Europe': [
        ('Austria', '/countries/austria'),
        ('Croatia', '/countries/croatia'),
        ('Czech Republic', '/countries/czech-republic'),
        ('Germany', '/countries/germany'),
        ('Hungary', '/countries/hungary'),
        ('Italy', '/countries/italy'),
        ('Poland', '/countries/poland'),
        ('Slovakia', '/countries/slovakia'),
        ('Slovenia', '/countries/slovenia'),
    ],
    'Danube': [
        ('Austria', '/countries/austria'),
        ('Bulgaria', '/countries/bulgaria'),
        ('Croatia', '/countries/croatia'),
        ('Czech Republic', '/countries/czech-republic'),
        ('Germany', '/countries/germany'),
        ('Hungary', '/countries/hungary'),
        ('Romania', '/countries/romania'),
        ('Slovakia', '/countries/slovakia'),
        ('Slovenia', '/countries/slovenia'),
        ('Bosnia and Herzegovina, ', ''),
        ('Montenegro', ''),
        ('Serbia', ''),
        ('Ukraine', ''),
        ('Republic of Moldova', ''),
    ],
    'Mediterranean': [
        ('Albania', ''),
        ('Bosnia and Herzegovina', ''),
        ('Croatia', '/countries/croatia'),
        ('Cyprus', '/countries/cyprus'),
        ('France', '/countries/france'),
        ('Greece', '/countries/greece'),
        ('Italy', '/countries/italy'),
        ('Malta', '/countries/malta'),
        ('Montenegro', ''),
        ('Portugal', '/countries/portugal'),
        ('Slovenia', '/countries/slovenia'),
        ('Spain', '/countries/spain'),
        ('United Kingdom', '/countries/united-kingdom'),
    ],
    'North Sea': [
        ('Belgium', '/countries/belgium'),
        ('Denmark', '/countries/denmark'),
        ('Germany', '/countries/germany'),
        ('Netherlands', '/countries/netherlands'),
        ('Sweden', '/countries/sweden'),
        ('United Kingdom', '/countries/united-kingdom'),
        ('Norway', '/countries/norway'),
    ],
    'North West Europe': [
        ('Belgium', '/countries/belgium'),
        ('France', '/countries/france'),
        ('Germany', '/countries/germany'),
        ('Ireland', '/countries/ireland'),
        ('Luxembourg', '/countries/luxembourg'),
        ('Netherlands', '/countries/netherlands'),
        ('Switzerland', '/countries/switzerland'),
        ('United Kingdom', '/countries/united-kingdom'),
    ],
    'South West Europe': [
        ('France', '/countries/france'),
        ('Portugal', '/countries/portugal'),
        ('Spain', '/countries/spain'),
        ('United Kingdom', '/countries/united-kingdom'),
        ('Andorra', ''),
    ],
    'Other regions': [
        ('', '')
    ],
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

        return sorted([{'url': b.getURL(), 'title': b.Title} for b in brains],
                      key=lambda x:x['title'])

    def countries(self):
        # a list of {'name': Country name, 'link': Country Link}
        region = self.data.get('region', None)
        if not region:
            return []
        return regions[region]
