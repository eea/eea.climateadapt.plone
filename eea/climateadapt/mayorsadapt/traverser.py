""" The token access traverser

URLs should look like /@@tk/<token value>/city-profile/somecity
"""

from Products.CMFPlone.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import timedelta
from eea.climateadapt.city_profile import TOKEN_COOKIE_NAME
from zExceptions import NotFound
from zope.publisher.browser import BrowserPage
import datetime


TIMEOUT = timedelta(hours=4)


class TokenTraverser(BrowserPage):
    """ Token Traverser page.

    URL is in form:
    http://cca.ro/cptk/eyJleHBpcmVzIjog...xaazk=/my-first-city

    /cptk/ is this class, TokenTraverser
    /<token>/ is TokenHandler
    /<cityid> is CityHandler
    """

    def publishTraverse(self, request, token):
        """ Sets the cookie with the token value, expires in 2 hours """

        return TokenHandler(self.context, request, token)


class TokenHandler(object):
    """ Stage 1 of the traverser
    """

    def __init__(self, context, request, token):
        self.context = context
        self.request = request
        self.token = token

    def __getitem__(self, cityname):
        catalog = getToolByName(self.context, 'portal_catalog')
        cities = catalog.unrestrictedSearchResults(
            portal_type='eea.climateadapt.city_profile',
            getId=cityname)

        if not cities:
            raise NotFound

        if len(cities) > 1:
            raise ValueError

        redir = CityHandler(cities[0], self.request)
        redir.token = self.token
        return redir


class CityHandler(BrowserPage):
    """ Redirect to a city. Last stage of the traverser

    Note: don't remove docstring, needed by Zope security
    """

    index = ViewPageTemplateFile('pt/redirect-to-city.pt')
    token = None

    def __init__(self, context, request):
        # context is a brain
        self.context = context
        self.request = request

    def __call__(self):
        expire_date = datetime.datetime.now() + TIMEOUT

        self.request.response.setCookie(
            TOKEN_COOKIE_NAME, self.token, expires=expire_date, path='/')

        self.url = self.context.getURL()
        return self.request.response.redirect(self.context.getURL())
        #return self.index()
