from zope.interface import classImplements

from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender


class AceItemView(DefaultView, AceViewApi):
    """
    """


class PublicationReportView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Publications and Reports"


class InformationPortalView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Information Portal"


class GuidanceDocumentView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Guidance Document"


class ToolView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Tools"


class IndicatorView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Indicator"


class OrganisationView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Organisation"


# Form Extenders + add/edit forms

class PublicationReportEditForm(DefaultEditForm):
    """ Edit form for Publication Reports
    """


class PublicationReportAddForm(DefaultAddForm):
    """ Add Form for Publication Reports
    """


PublicationReportEditView = layout.wrap_form(PublicationReportEditForm)
classImplements(PublicationReportEditView, IDexterityEditForm)


class PublicationReportFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]


class InformationPortalEditForm(DefaultEditForm):
    """ Edit form for Information Portals
    """


class InformationPortalAddForm(DefaultAddForm):
    """ Add Form for Information Portals
    """


InformationPortalEditView = layout.wrap_form(InformationPortalEditForm)
classImplements(InformationPortalEditView, IDexterityEditForm)


class InformationPortalFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]


class GuidanceDocumentEditForm(DefaultEditForm):
    """ Edit form for Guidance Documents
    """


class GuidanceDocumentAddForm(DefaultAddForm):
    """ Add Form for Guidance Documents
    """


GuidanceDocumentEditView = layout.wrap_form(GuidanceDocumentEditForm)
classImplements(GuidanceDocumentEditView, IDexterityEditForm)


class GuidanceDocumentFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]


class ToolEditForm(DefaultEditForm):
    """ Edit form for Tools
    """


class ToolAddForm(DefaultAddForm):
    """ Add Form for Tools
    """


ToolEditView = layout.wrap_form(ToolEditForm)
classImplements(ToolEditView, IDexterityEditForm)


class ToolFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]


class IndicatorEditForm(DefaultEditForm):
    """ Edit form for Indicators
    """


class IndicatorAddForm(DefaultAddForm):
    """ Add Form for Indicators
    """


IndicatorEditView = layout.wrap_form(IndicatorEditForm)
classImplements(IndicatorEditView, IDexterityEditForm)


class IndicatorFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]


class OrganisationEditForm(DefaultEditForm):
    """ Edit form for Organisations
    """


class OrganisationAddForm(DefaultAddForm):
    """ Add Form for Organisations
    """


OrganisationEditView = layout.wrap_form(OrganisationEditForm)
classImplements(OrganisationEditView, IDexterityEditForm)


class OrganisationFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.remove('IPublication.effective')
        self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_dates', 'label_schema_ownership']
        self.form.groups = [group for group in self.form.groups if group.label not in labels]
