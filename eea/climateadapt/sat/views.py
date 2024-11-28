from eea.climateadapt.browser.misc import ISimplifiedResourceRegistriesView
from Products.Five.browser import BrowserView
# from zope.interface import implementer

raise ValueError("Should not be imported")


class SatView(BrowserView):
    """A http://climate-adapt.eea.europa.eu/sat custom view"""

    implements(ISimplifiedResourceRegistriesView)
