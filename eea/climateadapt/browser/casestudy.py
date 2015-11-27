from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi


class CaseStudyView(DefaultView, AceViewApi):
    def __call__(self):
        return super(CaseStudyView, self).__call__()
