from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class ISatView(Interface):
    """ Marker interface ISatView"""


class SatView(BrowserView):
    """ A http://climate-adapt.eea.europa.eu/sat custom view """
    implements(ISatView)
