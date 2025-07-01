# TODO: cleanup this file, it seems to have been scraped
from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi
from plone.z3cform import layout
from zope.interface import classImplements
from plone.z3cform.fieldsets.extensible import FormExtender
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.interfaces import IDexterityEditForm


class AceProjectView(DefaultView, AceViewApi):
    type_label = "Project"


class AceProjectEditForm(DefaultEditForm):
    """Edit form for Ace Projects"""


class AceProjectAddForm(DefaultAddForm):
    """Add Form for Ace Projects"""


AceProjectEditView = layout.wrap_form(AceProjectEditForm)
classImplements(AceProjectEditView, IDexterityEditForm)


class AceProjectFormExtender(FormExtender):
    def update(self):
        self.move("IRelatedItems.relatedItems", after="partners_source_link")
        self.remove("ICategorization.subjects")
        self.remove("ICategorization.language")
        self.remove("IPublication.effective")
        self.remove("IPublication.expires")
        self.remove("IOwnership.creators")
        self.remove("IOwnership.contributors")
        self.remove("IOwnership.rights")
        self.remove("IBlocks.blocks")
        self.remove("IBlocks.blocks_layout")
        labels = ["label_schema_dates", "label_schema_ownership", "Layout", "Settings"]
        self.form.groups = [
            group for group in self.form.groups if group.label not in labels
        ]
