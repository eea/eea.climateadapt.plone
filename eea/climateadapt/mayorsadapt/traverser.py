""" The token access traverser

URLs should look like /@@tk/<token value>/city-profile/somecity
"""


from zope.publisher.browser import BrowserPage
from eea.climateadapt.city_profile import TOKENID
from eea.climateadapt.city_profile import expire_date


class TokenTraverser(BrowserPage):
    def publishTraverse(self, request, name):
        request.SESSION.set(TOKENID, name)
        request.RESPONSE.setCookie(TOKENID, name, expires=expire_date)
        return self.context
