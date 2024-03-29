""" A tile to implement the countries select dropdown
"""

import json

from collective.cover.tiles.base import (IPersistentCoverTile,
                                         PersistentCoverTile)
from eea.climateadapt.vocabulary import ace_countries_selection
from plone.memoize import view
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implements


class ICountrySelectTile(IPersistentCoverTile):

    title = schema.TextLine(
        title=u'Title',
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

    @view.memoize
    def is_empty(self):
        return False

    @view.memoize
    def countries(self):

        # countries = [(c[0], c[1].replace(" ", "-")) for c in
        #              ace_countries_selection]

        # return sorted(countries, key=lambda c: c[1])
        clist = filter(lambda country:  country[0] != 'GB', ace_countries_selection)
        return sorted(clist, key=lambda c: c[1])


class SettingsPage(BrowserView):
    """ JSON for settings for country headers
    """

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        id = self.context.id.replace("-", " ").title()
        if id == 'Turkiye':
            id = 'Turkey'
        res = {'focusCountry': id}

        return json.dumps(res)
