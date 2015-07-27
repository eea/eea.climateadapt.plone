#from Products.Five import BrowserView
from plone.dexterity.browser.view import DefaultView

class AceItemView(DefaultView):
    def __call__(self):
        return super(AceItemView, self).__call__()
