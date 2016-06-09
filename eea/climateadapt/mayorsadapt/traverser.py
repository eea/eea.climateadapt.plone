""" The token access traverser

URLs should look like /@@tk/<token value>/city-profile/somecity
"""

from zope.publisher.browser import BrowserPage
from eea.climateadapt.city_profile import TOKENID
from datetime import timedelta
import datetime


class TokenTraverser(BrowserPage):
    def publishTraverse(self, request, name):
        """ Sets the cookie with the token value, expires in 2 hours """
        expire_date = datetime.datetime.now() + timedelta(hours=2)
        #request.SESSION.set(TOKENID, name)
        request.RESPONSE.setCookie(TOKENID, name, expires=expire_date)
        return self.context
