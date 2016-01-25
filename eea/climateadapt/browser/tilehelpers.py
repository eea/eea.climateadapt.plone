""" Views to be used by tiles.

It helps to separate the tiles from the views, those views can be easier
developed and tested.
"""

from eea.climateadapt.vocabulary import ace_countries
from Products.Five.browser import BrowserView


class AceContentSearch(BrowserView):
    """ A view to show an AceContet "portlet" search
    """


class FrontPageCountries(BrowserView):
    """ A view to render the frontpage tile with countries and country select
    form
    """

    def countries(self):
        return ace_countries
