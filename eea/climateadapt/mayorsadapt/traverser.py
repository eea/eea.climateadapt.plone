""" The token access traverser

URLs should look like /@@tk/<token value>/city-profile/somecity
"""


from zope.publisher.browser import BrowserPage


class TokenTraverser(BrowserPage):
    def publishTraverse(self, request, name):
        request.SESSION.set('tk', name)
        return self.context

