from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi


class AceProjectView(DefaultView, AceViewApi):
    def __call__(self):
        return super(AceProjectView, self).__call__()

    def linkify(self, text):
        if not text:
            return
        if text.startswith('http'):
            return text
        return "http://" + text

    def website_links(self, text):
        return text
