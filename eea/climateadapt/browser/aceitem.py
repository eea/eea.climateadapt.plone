# from Products.Five import BrowserView
from plone.dexterity.browser.view import DefaultView
from eea.climateadapt.browser import AceViewApi


class AceItemView(DefaultView, AceViewApi):
    """
    """
    # def __call__(self):
    #     return super(AceItemView, self).__call__()


class PublicationReportView(DefaultView, AceViewApi):
    """
    """

    # def __call__(self):
    #     return super(PublicationReportView).__call__()


class InformationPortalView(DefaultView, AceViewApi):
    """
    """

    # def __call__(self):
    #     return super(InformationPortalView).__call__()


class GuidanceDocumentView(DefaultView, AceViewApi):
    """
    """

    # def __call__(self):
    #     return super(GuidanceDocumentView).__call__()


class ToolView(DefaultView, AceViewApi):
    """
    """

    # def __call__(self):
    #     return super(ToolView).__call__()


class OrganisationView(DefaultView, AceViewApi):
    """
    """

    # def __call__(self):
    #     return super(OrganisationView).__call__()
