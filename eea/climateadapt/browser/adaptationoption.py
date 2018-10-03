from zope.component import getUtility
from zope.interface import classImplements
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission

import plone.api as api
from Acquisition import aq_inner
from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zc.relation.interfaces import ICatalog


class AdaptationOptionView(DefaultView, AceViewApi):
    """ """

    type_label = u"Adaptation option"

    def get_related_casestudies(self):
        titles = []
        urls = []
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)

        for rel in catalog.findRelations(
                    dict(to_id=intids.getId(aq_inner(self.context)),
                         from_attribute='adaptationoptions')
                ):
            obj = intids.queryObject(rel.from_id)

            if obj is not None and checkPermission('zope2.View', obj):
                obj_state = api.content.get_state(obj)

                if obj_state == 'published':
                    titles.append(obj.title)
                    urls.append(obj.absolute_url())

        return {'url': urls, 'title': titles}


class AdaptationOptionFormExtender(FormExtender):
    def update(self):
        self.move('description', before='long_description')
        self.move('category', before='stakeholder_participation')
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups
                            if group.label not in labels]


class AdaptationOptionEditForm(DefaultEditForm):
    """ Edit form for case studies
    """


AdaptationOptionEditView = layout.wrap_form(AdaptationOptionEditForm)
classImplements(AdaptationOptionEditView, IDexterityEditForm)


class AdaptationOptionAddForm(DefaultAddForm):
    """ Add Form for case studies
    """
