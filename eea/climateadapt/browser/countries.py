import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class ICountriesView (Interface):
    """ Countries Interface """


class CountriesView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/countries """

    implements(ICountriesView)
