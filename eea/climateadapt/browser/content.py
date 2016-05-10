import os
from zope.interface import Interface
from zope.interface import implements
from Products.Five.browser import BrowserView


class IContentView (Interface):
    """ /content Interface """


class ContentView (BrowserView):
    """ Custom view for /content """

    implements(IContentView)

    def __call__(self):
        return self.request.response.redirect('/data-and-downloads')
