from eea.climateadapt.browser import AceViewApi
from plone.dexterity.browser.view import DefaultView


class AceItemView(DefaultView, AceViewApi):
    """
    """


class PublicationReportView(DefaultView, AceViewApi):
    """
    """


class InformationPortalView(DefaultView, AceViewApi):
    """
    """


class GuidanceDocumentView(DefaultView, AceViewApi):
    """
    """

    def link_to_original(self):
        """ Returns link to original object, to allow easy comparison
        """

        return "http://adapt-test.eea.europa.eu/viewaceitem?aceitem_id=%s" % \
            self.context._aceitem_id


class ToolView(DefaultView, AceViewApi):
    """
    """


class OrganisationView(DefaultView, AceViewApi):
    """
    """

