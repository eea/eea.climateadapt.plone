from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.vocabulary import _relevance
from plone.dexterity.browser.view import DefaultView


class CaseStudyView(DefaultView, AceViewApi):
    def __call__(self):
        return super(CaseStudyView, self).__call__()

    def get_adaptation_options(self):
        # TODO: filter by published
        return [o.to_object for o in self.context.adaptationoptions]

    def relevances_dict(self):
        return dict(_relevance)
