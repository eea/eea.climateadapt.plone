from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.view import DefaultView


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


class MapGraphDatasetView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Map Graph Data Set"


class IndicatorView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Indicator"


class OrganisationView(DefaultView, AceViewApi):
    """
    """
    type_label = u"Organisation"
