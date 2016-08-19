""" The token access traverser

URLs should look like /@@tk/<token value>/city-profile/somecity
"""

from Products.CMFPlone.utils import getToolByName
from datetime import timedelta
from eea.climateadapt.city_profile import TOKEN_COOKIE_NAME
from zExceptions import NotFound
from zope.publisher.browser import BrowserPage
import datetime


TIMEOUT = timedelta(hours=2)


class TokenCityRedirect(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        url = self.context.absolute_url()
        import pdb; pdb.set_trace()
        return self.request.response.redirect(url)


class TokenCityTraverser(object):

    def __init__(self, context, request, token):
        self.context = context
        self.request = request
        self.token = token

    def __getitem__(self, cityname):
        expire_date = datetime.datetime.now() + TIMEOUT
        self.request.RESPONSE.setCookie(
            TOKEN_COOKIE_NAME, cityname, expires=expire_date)

        catalog = getToolByName(self.context, 'portal_catalog')
        cities = catalog.unrestrictedSearchResults(
            portal_type='eea.climateadapt.city_profile',
            getId=cityname)

        if not cities:
            raise NotFound

        if len(cities) > 1:
            raise ValueError

        import pdb; pdb.set_trace()
        obj = cities[0].getObject()
        return TokenCityRedirect(obj, self.request)


class TokenTraverser(BrowserPage):
    """ Token Traverser page.

    TODO: explain mechanism
    """

    def publishTraverse(self, request, token):
        """ Sets the cookie with the token value, expires in 2 hours """

        return TokenCityTraverser(self.context, request, token)
