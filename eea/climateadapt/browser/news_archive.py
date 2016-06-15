from Products.Five.browser import BrowserView
# from zope.interface import Interface


class NewsArchiveView (BrowserView):
    """ Custom view for news
    """

    def __call__(self):
        return self.index()
