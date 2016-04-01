import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class IAdaptationStrategy (Interface):
    """ Countries Interface """


class AdaptationStrategyView (BrowserView):
    """ Redirect for http://climate-adapt.eea.europa.eu/adaptation-strategies
        to /countries-view-map
    """

    implements(IAdaptationStrategy)

    def __call__(self):
        return self.request.response.redirect('/countries-view-map')
