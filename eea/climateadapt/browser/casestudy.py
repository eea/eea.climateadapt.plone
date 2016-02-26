from Products.CMFPlone.utils import getToolByName
from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.vocabulary import _relevance
from plone.dexterity.browser.view import DefaultView


class CaseStudyView(DefaultView, AceViewApi):
    def __call__(self):
        return super(CaseStudyView, self).__call__()

    def get_adaptation_options(self):
        options = self.context.adaptationoptions

        cat = getToolByName(self.context, 'portal_catalog')
        res = []
        for v in options:
            res.extend(cat.searchResults(acemeasure_id=v))

        return res

    def relevances_dict(self):
        return dict(_relevance)

