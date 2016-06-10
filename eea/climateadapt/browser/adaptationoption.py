from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform.fieldsets.extensible import FormExtender
from plone.z3cform import layout
from zope.interface import classImplements


class AdaptationOptionView(DefaultView, AceViewApi):
    """ """

    type_label = u"Adaptation option"


class AdaptationOptionFormExtender(FormExtender):
    def update(self):
        self.move('category', before='stakeholder_participation')


class AdaptationOptionEditForm(DefaultEditForm):
    """ Edit form for case studies
    """

AdaptationOptionEditView = layout.wrap_form(AdaptationOptionEditForm)
classImplements(AdaptationOptionEditView, IDexterityEditForm)


class AdaptationOptionAddForm(DefaultAddForm):
    """ Add Form for case studies
    """
