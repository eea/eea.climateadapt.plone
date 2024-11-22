from plone.dexterity.browser.add import DefaultAddForm
from plone.z3cform.fieldsets.extensible import FormExtender


class NewsItemAddForm(DefaultAddForm):
    """"""

# AddView = layout.wrap_form(AddForm)
# classImplements(AddView, IAddForm)


class NewsItemAddExtender(FormExtender):
    def update(self):
        self.remove('IBlocks.blocks')
        self.remove('IBlocks.blocks_layout')
        groups = self.form.groups
        self.form.groups = [
            group
            for group in groups
            if len(list(group.fields.values())) > 0]
