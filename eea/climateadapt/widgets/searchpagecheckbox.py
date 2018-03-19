from eea.facetednavigation.widgets import ViewPageTemplateFile
from eea.facetednavigation.widgets.checkbox.widget import \
    Widget as BaseCheckboxWidget
from Products.Archetypes.public import Schema, StringField

EditSchema = Schema((

    StringField(
        'disable_criterion_label',
        schemata='default',
        required=True,
    ),
    StringField(
        'enable_criterion_label',
        schemata='default',
        required=True,
    ),

))


class SearchPageCheckbox(BaseCheckboxWidget):
    widget_type = 'searchpagecheckbox'
    index = ViewPageTemplateFile('searchpagecheckbox.pt')

    # edit_schema = BaseCheckboxWidget.edit_schema.copy() + EditSchema

    # def __init__(self, context, request, data=None):
    #     self.context = context
    #     self.request = request
    #     self.request.debug = False
    #     self.data = data

    @property
    def disable_label(self):
        return self.data.get('disable_criterion_label','disable')

    @property
    def enable_label(self):
        return self.data.get('enable_criterion_label','enable')
