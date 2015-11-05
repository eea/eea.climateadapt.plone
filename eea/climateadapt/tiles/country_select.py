""" A tile to implement the countries select dropdown
"""

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.base import PersistentCoverTile
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.vocabulary import ace_countries
from zope import schema
from zope.interface import implements


class ICountrySelectTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=_(u'Title'),
        required=False,
    )


class CountrySelectTile(PersistentCoverTile):
    """ CountrySelect tile

    Shows a dropdown select for a region
    """

    implements(ICountrySelectTile)

    index = ViewPageTemplateFile('pt/country_select.pt')

    is_configurable = False
    is_editable = False
    is_droppable = False
    short_name = u'Select country'

    def is_empty(self):
        return False

    def countries(self):

        return ace_countries
