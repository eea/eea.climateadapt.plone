from eea.climateadapt.browser.misc import ISimplifiedResourceRegistriesView
from Products.Five.browser import BrowserView
from zope.interface import implements


class SatView(BrowserView):
    """ A http://climate-adapt.eea.europa.eu/sat custom view """

    implements(ISimplifiedResourceRegistriesView)
