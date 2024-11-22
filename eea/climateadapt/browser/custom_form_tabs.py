from plone.dexterity.browser import add
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zope.interface import classImplements

# from z3c.form.interfaces import IAddForm


class CustomFormTabsEditForm(DefaultEditForm):
    """ Simplify tabs in Edit forms of dexterity items
        Exclude Layout (containing fields: blocks and blocks_layout)

        This will prevent collapsing the tabs as select

        See: max_tabs in form_tabbing.js
        var ploneFormTabbing = {
            // standard jQueryTools configuration options for all form tabs
            jqtConfig:{current:'selected'},
            max_tabs: 6
        };
    """


CustomFormTabsEditView = layout.wrap_form(CustomFormTabsEditForm)
classImplements(CustomFormTabsEditView, IDexterityEditForm)


class CustomFormTabsFormExtender(FormExtender):
    def update(self):
        self.remove('IBlocks.blocks')
        self.remove('IBlocks.blocks_layout')
        groups = self.form.groups
        self.form.groups = [group for group in groups if len(
            list(group.fields.values())) > 0]


class EventAddForm(add.DefaultAddForm):
    """"""

# AddView = layout.wrap_form(AddForm)
# classImplements(AddView, IAddForm)


class EventAddExtender(FormExtender):
    def update(self):
        self.remove('IBlocks.blocks')
        self.remove('IBlocks.blocks_layout')
        groups = self.form.groups
        self.form.groups = [
            group
            for group in groups
            if len(list(group.fields.values())) > 0]


# class AddForm(add.DefaultAddForm):
#     """"""
#     portal_type = 'Event'


# class AddView(
#     # add.DefaultAddView
#     FormExtender
#     ):
#     form = AddForm

#     def update(self):
#         # import pdb; pdb.set_trace()
#         self.remove('IBlocks.blocks')
#         self.remove('IBlocks.blocks_layout')
#         groups = self.form.groups
#         self.form.groups = [group for group in groups if len(
#             group.fields.values()) > 0]

#         super(AddView, self).update()
