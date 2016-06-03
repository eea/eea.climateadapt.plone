from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.vocabulary import _relevance
from plone.dexterity.browser.view import DefaultView
from plone.z3cform.fieldsets.extensible import FormExtender


class CaseStudyView(DefaultView, AceViewApi):
    def __call__(self):
        return super(CaseStudyView, self).__call__()

    def get_adaptation_options(self):
        # TODO: filter by published
        return [o.to_object for o in self.context.adaptationoptions]

    def relevances_dict(self):
        return dict(_relevance)


class CaseStudyEditFormExtender(FormExtender):
    def update(self):
        self.move('IGeolocatable.geolocation', after='geochars')
        self.move('adaptationoptions', after='lifetime')
        self.move('primary_photo', after='long_description')
