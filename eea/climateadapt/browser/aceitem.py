from zope.component import queryMultiAdapter  # getMultiAdapter,
from zope.interface import classImplements  # , implements
from zope.publisher.interfaces import NotFound

from eea.climateadapt.browser import AceViewApi
from eea.depiction.browser.dexterity import DexterityImageView
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender

from zope.interface import implements
from Products.Five.browser import BrowserView
from eea.depiction.browser.interfaces import IImageView
from zope.publisher.interfaces import NotFound
from zope.component import queryMultiAdapter


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


class InformationPortalEditForm(DefaultEditForm):
    """ Edit form for Information Portals
    """


class InformationPortalAddForm(DefaultAddForm):
    """ Add Form for Information Portals
    """


InformationPortalEditView = layout.wrap_form(InformationPortalEditForm)
classImplements(InformationPortalEditView, IDexterityEditForm)


class GuidanceDocumentEditForm(DefaultEditForm):
    """ Edit form for Guidance Documents
    """


class GuidanceDocumentAddForm(DefaultAddForm):
    """ Add Form for Guidance Documents
    """


GuidanceDocumentEditView = layout.wrap_form(GuidanceDocumentEditForm)
classImplements(GuidanceDocumentEditView, IDexterityEditForm)


class ToolEditForm(DefaultEditForm):
    """ Edit form for Tools
    """


class ToolAddForm(DefaultAddForm):
    """ Add Form for Tools
    """


ToolEditView = layout.wrap_form(ToolEditForm)
classImplements(ToolEditView, IDexterityEditForm)


class IndicatorEditForm(DefaultEditForm):
    """ Edit form for Indicators
    """


class IndicatorAddForm(DefaultAddForm):
    """ Add Form for Indicators
    """


IndicatorEditView = layout.wrap_form(IndicatorEditForm)
classImplements(IndicatorEditView, IDexterityEditForm)


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
        self.move('IRelatedItems.relatedItems', before='comments')
        self.move('acronym', before='title')


class AceItemFormExtender(FormExtender):
    def update(self):
        self.remove('ICategorization.subjects')
        self.remove('ICategorization.language')
        self.move('IRelatedItems.relatedItems', after='comments')
        self.move('source', after='contributors')
        # Add the IPublication behavior if you want them, it's not enabled
        # except for the IIndicator, right now
        # self.remove('IPublication.effective')
        # self.remove('IPublication.expires')
        self.remove('IOwnership.creators')
        self.remove('IOwnership.contributors')
        self.remove('IOwnership.rights')
        labels = ['label_schema_ownership']     # 'label_schema_dates',
        self.form.groups = [group
                            for group in self.form.groups

                            if group.label not in labels]


class CCAContentDepictionView(DexterityImageView):
    """ Get cover image from folder contents
    """

    _field = "image"

    @property
    def img(self):
        """
        """
        return self.context

    @property
    def field(self):
        """ Image field
        """
        return getattr(self.context, self._field)

    def __call__(self, scalename='thumb'):
        if not self.display(scalename):
            raise NotFound(self.request, scalename)

        scaleview = queryMultiAdapter((self.img, self.request), name='images')
        scale = scaleview.scale(self._field, scale=scalename)

        return scale or ""
