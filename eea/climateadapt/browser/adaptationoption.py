from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi
from plone.z3cform.fieldsets.extensible import FormExtender


class AdaptationOptionView(DefaultView, AceViewApi):
    """ """

    type_label = u"Adaptation option"


class AdaptationOptionEditFormExtender(FormExtender):
    def update(self):
        self.move('category', before='stakeholder_participation')
