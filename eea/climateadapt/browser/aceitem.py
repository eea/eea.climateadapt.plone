# import json
# import urllib

from eea.climateadapt.browser import AceViewApi
from eea.climateadapt.browser.misc import create_contributions_link
# from eea.climateadapt.translation.core import get_translation_object
# from eea.climateadapt.translation.utils import get_current_language
from plone import api
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zc.relation.interfaces import ICatalog
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.interface import classImplements
from zope.intid.interfaces import IIntIds

# from itertools import chain, islice
# from eea.depiction.browser.interfaces import IImageView
# from Products.Five.browser import BrowserView


class AceItemView(DefaultView, AceViewApi):
    """"""


class PublicationReportView(DefaultView, AceViewApi):
    """"""

    type_label = "Publications and Reports"


class InformationPortalView(DefaultView, AceViewApi):
    """"""

    type_label = "Information Portal"


class GuidanceDocumentView(DefaultView, AceViewApi):
    """"""

    type_label = "Guidance Document"


class ToolView(DefaultView, AceViewApi):
    """"""

    type_label = "Tools"


class IndicatorView(DefaultView, AceViewApi):
    """"""

    type_label = "Indicator"


class C3sIndicatorView(DefaultView, AceViewApi):
    """"""

    type_label = "C3s Indicator"

    def c3sjs_overview(self):
        response = """
            const WORKFLOW = 'SCRIPT_JSON';
            const WORKFLOWPARAMS = {};
            (function () {
                document.addEventListener('DOMContentLoaded', function () {
                    window.cds_toolbox.runApp(
                        'toolbox-app',
                        WORKFLOW,
                        {
                            workflowParams: WORKFLOWPARAMS,
                        }
                    );
                }, false);
            })();
            """
        response = response.replace(
            "SCRIPT_JSON", self.context.overview_app_toolbox_url
        )
        return response

    def c3sjs_details(self):
        response = """
                    var c3s_details_url  = '{0}';
                    var c3s_details_params  = {1};
                """.format(
            self.context.details_app_toolbox_url, self.context.details_app_parameters
        )
        return response

    def get_toolbox_embed_version(self):
        site = api.portal.get()
        base_folder = site["en"]["knowledge"]["european-climate-data-explorer"]
        annot = IAnnotations(base_folder)
        if "c3s_json_data" in annot:
            return annot["c3s_json_data"]["data"]["toolbox_embed_version"]
        return "4.16.0"


class OrganisationView(DefaultView, AceViewApi):
    """"""

    type_label = "Organisation"

    def __init__(self, context, request):
        # Each view instance receives context and request as construction parameters
        self.context = context
        self.request = request

    def is_observatory_page(self):
        if self.request.form.get("only_article") == "1":
            return 1
        if self.request.form.get("observatory_page") == "1":
            return 1
        return 0

    def to_observatory_url(self, obj):
        # TODO get current language
        # current_language = get_current_language(self.context, self.request)
        current_language = "en"
        segments = obj.getPhysicalPath()[2:]
        if segments[0] != "metadata":
            segments = segments[1:]
        return "/" + current_language + "/observatory/++aq++" + "/".join(segments)

    def get_contributions(self):
        # TODO get current language
        # current_language = get_current_language(self.context, self.request)
        current_language = "en"
        if current_language != "en":
            # TODO get translation object
            # en_obj = get_translation_object(self.context, "en")
            en_obj = self.context
        else:
            en_obj = self.context

        relation_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        uid = intids.getId(en_obj.aq_inner.aq_self)
        response = []
        urls = []

        contributors = list(relation_catalog.findRelations({"to_id": uid}))
        for relation in contributors:
            if relation.from_attribute == "relatedItems":
                continue

            engl_obj = relation.from_object
            # TODO get translation object
            # obj = get_translation_object(engl_obj, current_language)
            obj = engl_obj
            if obj is not None:
                if api.content.get_state(obj) == "published":
                    if obj.absolute_url() in urls or (
                        not getattr(obj, "include_in_observatory")
                    ):
                        continue

                    urls.append(obj.absolute_url())
                    response.append(
                        {
                            "title": obj.title,
                            "url": self.to_observatory_url(obj),
                            "date": (
                                getattr(obj, "publication_date", None)
                                or obj.creation_date.asdatetime().date()
                            ),
                        }
                    )

        # print(response)
        response.sort(key=lambda x: x.get("date"), reverse=True)
        return response

    def contributions_link(self):
        return create_contributions_link("en", self.context.id)


# Form Extenders + add/edit forms


class PublicationReportEditForm(DefaultEditForm):
    """Edit form for Publication Reports"""


class PublicationReportAddForm(DefaultAddForm):
    """Add Form for Publication Reports"""


PublicationReportEditView = layout.wrap_form(PublicationReportEditForm)
classImplements(PublicationReportEditView, IDexterityEditForm)


class InformationPortalEditForm(DefaultEditForm):
    """Edit form for Information Portals"""


class InformationPortalAddForm(DefaultAddForm):
    """Add Form for Information Portals"""


InformationPortalEditView = layout.wrap_form(InformationPortalEditForm)
classImplements(InformationPortalEditView, IDexterityEditForm)


class GuidanceDocumentEditForm(DefaultEditForm):
    """Edit form for Guidance Documents"""


class GuidanceDocumentAddForm(DefaultAddForm):
    """Add Form for Guidance Documents"""


GuidanceDocumentEditView = layout.wrap_form(GuidanceDocumentEditForm)
classImplements(GuidanceDocumentEditView, IDexterityEditForm)


class ToolEditForm(DefaultEditForm):
    """Edit form for Tools"""


class ToolAddForm(DefaultAddForm):
    """Add Form for Tools"""


ToolEditView = layout.wrap_form(ToolEditForm)
classImplements(ToolEditView, IDexterityEditForm)


class IndicatorEditForm(DefaultEditForm):
    """Edit form for Indicators"""


class IndicatorAddForm(DefaultAddForm):
    """Add Form for Indicators"""


IndicatorEditView = layout.wrap_form(IndicatorEditForm)
classImplements(IndicatorEditView, IDexterityEditForm)


class C3sIndicatorEditForm(DefaultEditForm):
    """Edit form for C3sIndicators"""


class C3sIndicatorAddForm(DefaultAddForm):
    """Add Form for C3sIndicators"""


C3sIndicatorEditView = layout.wrap_form(IndicatorEditForm)
classImplements(C3sIndicatorEditView, IDexterityEditForm)


class OrganisationEditForm(DefaultEditForm):
    """Edit form for Organisations"""


class OrganisationAddForm(DefaultAddForm):
    """Add Form for Organisations"""


OrganisationEditView = layout.wrap_form(OrganisationEditForm)
classImplements(OrganisationEditView, IDexterityEditForm)


class OrganisationFormExtender(FormExtender):
    def update(self):
        self.move("logo", before="image")
        self.move("IRelatedItems.relatedItems", before="comments")
        self.move("acronym", before="title")
        self.move("organisational_contact_information", after="include_in_observatory")
        self.move("organisational_websites", after="include_in_observatory")
        self.move("organisational_key_activities", after="include_in_observatory")
        self.remove("other_contributor")
        self.remove("IBlocks.blocks")
        self.remove("IBlocks.blocks_layout")
        labels = ["label_schema_ownership", "Settings"]
        self.form.groups = [
            group
            for group in self.form.groups
            if (group.label not in labels and len(list(group.fields.values())) > 0)
        ]


class AceItemFormExtender(FormExtender):
    def update(self):
        self.remove("ICategorization.subjects")
        self.remove("ICategorization.language")
        self.move("IRelatedItems.relatedItems", after="comments")
        # Add the IPublication behavior if you want them, it's not enabled
        # except for the IIndicator, right now
        # self.remove('IPublication.effective')
        # self.remove('IPublication.expires')
        self.remove("IOwnership.creators")
        self.remove("IOwnership.contributors")
        self.remove("IOwnership.rights")
        self.remove("IBlocks.blocks")
        self.remove("IBlocks.blocks_layout")
        # 'label_schema_dates',
        labels = ["label_schema_ownership", "Settings"]
        self.form.groups = [
            group
            for group in self.form.groups
            if (group.label not in labels and len(list(group.fields.values())) > 0)
        ]


class IndicatorFormExtender(FormExtender):
    def update(self):
        self.move("publication_date", before="map_graphs")
        self.remove("IBlocks.blocks")
        self.remove("IBlocks.blocks_layout")


class C3sIndicatorFormExtender(FormExtender):
    """Add Form for C3sIndicator"""

    def update(self):
        self.move("IRelatedItems.relatedItems", after="details_app_parameters")
        self.remove("IBlocks.blocks")
        self.remove("IBlocks.blocks_layout")
