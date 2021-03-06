import json
import urllib
from itertools import chain, islice

from eea.climateadapt.browser import AceViewApi
from plone import api
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.view import DefaultView
from plone.dexterity.interfaces import IDexterityEditForm
from plone.z3cform import layout
from plone.z3cform.fieldsets.extensible import FormExtender
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.interface import classImplements  # , implements
from zope.intid.interfaces import IIntIds

# from zope.interface import implements
# from eea.depiction.browser.interfaces import IImageView
# from Products.Five.browser import BrowserView


class AceItemView(DefaultView, AceViewApi):
    """"""


class PublicationReportView(DefaultView, AceViewApi):
    """"""

    type_label = u"Publications and Reports"


class InformationPortalView(DefaultView, AceViewApi):
    """"""

    type_label = u"Information Portal"


class GuidanceDocumentView(DefaultView, AceViewApi):
    """"""

    type_label = u"Guidance Document"


class ToolView(DefaultView, AceViewApi):
    """"""

    type_label = u"Tools"


class IndicatorView(DefaultView, AceViewApi):
    """"""

    type_label = u"Indicator"


class C3sIndicatorView(DefaultView, AceViewApi):
    """"""

    type_label = u"C3s Indicator"

    def c3sjs_overview(self):
        response = """(function () {
                    document.addEventListener('DOMContentLoaded', function () {
                        window.cds_toolbox.runApp('toolbox-app-overview', 'SCRIPT_URL', SCRIPT_JSON);
                    }, false);
                })();
                """
        response = response.replace("SCRIPT_URL", self.context.overview_app_toolbox_url)
        response = response.replace("SCRIPT_JSON", self.context.overview_app_parameters)
        return response

    def c3sjs_details(self):
        response = """
                    var c3s_details_url  = '{0}';
                    var c3s_details_params  = {1};
                """.format(
            self.context.details_app_toolbox_url, self.context.details_app_parameters
        )
        return response


def to_observatory_url(obj):
    return "/observatory/++aq++" + "/".join(obj.getPhysicalPath()[2:])


class OrganisationView(DefaultView, AceViewApi):
    """"""

    type_label = u"Organisation"

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

    def get_contributions(self):
        relation_catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        uid = intids.getId(self.context)
        response = []
        urls = []

        contributors = list(relation_catalog.findRelations({"to_id": uid}))
        for relation in contributors:
            if relation.from_attribute == "relatedItems":
                continue

            obj = relation.from_object
            if api.content.get_state(obj) == "published":
                if obj.absolute_url() in urls or (
                    not getattr(obj, "include_in_observatory")
                ):
                    continue

                urls.append(obj.absolute_url())
                response.append(
                    {
                        "title": obj.title,
                        "url": to_observatory_url(obj),
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
        org = ""

        map_contributor_values = {
            "copernicus-climate-change-service-ecmw": "Copernicus Climate Change Service and Copernicus Atmosphere Monitoring Service",
            "european-centre-for-disease-prevention-and-control-ecdc": "European Centre for Disease Prevention and Control",
            "european-commission": "European Commission",
            "european-environment-agency-eea": "European Environment Agency",
            "european-food-safety-authority": "European Food Safety Authority",
            "lancet-countdown": "Lancet Countdown",
            "who-regional-office-for-europe-who-europe": "WHO Regional Office for Europe",
            "world-health-organization": "World Health Organization",
        }

        if self.context.id in map_contributor_values:
            org = map_contributor_values[self.context.id]

        t = {
            u"function_score": {
                u"query": {
                    u"bool": {
                        u"filter": {
                            u"bool": {
                                u"should": [{u"term": {u"partner_contributors": org}}]
                            }
                        },
                    }
                }
            }
        }

        q = {"query": t}

        return "/observatory/catalogue/?source=" + urllib.quote(json.dumps(q))


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
        labels = ["label_schema_ownership"]  # 'label_schema_dates',
        self.form.groups = [
            group for group in self.form.groups if group.label not in labels
        ]


class IndicatorFormExtender(FormExtender):
    def update(self):
        self.move("publication_date", before="map_graphs")


class C3sIndicatorFormExtender(FormExtender):
    """Add Form for C3sIndicator"""

    def update(self):
        self.move("IRelatedItems.relatedItems", after="details_app_parameters")
