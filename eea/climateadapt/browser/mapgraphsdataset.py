from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.view import DefaultView
from plone.z3cform.fieldsets.extensible import FormExtender
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.add import DefaultAddForm
from plone.z3cform import layout
from zope.interface import classImplements
from plone.dexterity.interfaces import IDexterityEditForm


class MapGraphDatasetView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Map Graph Data Set"

    def compose_layer_link(self):
        pass
        # import pdb; pdb.set_trace( )


class MapsEditForm(DefaultEditForm):
    """ Edit form for case studies
    """


MapsEditView = layout.wrap_form(MapsEditForm)
classImplements(MapsEditView, IDexterityEditForm)


class MapsAddForm(DefaultAddForm):
    """ Add Form for case studies
    """


class MapsFormExtender(FormExtender):
    def update(self):
        self.move('gis_layer_id', after='websites')
