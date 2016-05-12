import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class ITransRegionView (Interface):
    """ Transnational regions Interface """


class TransRegionView (BrowserView):
    """ Custom view for http://climate-adapt.eea.europa.eu/transnational-regions """

    implements(ITransRegionView)
