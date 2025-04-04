from eea.climateadapt.behaviors import (
    IAction,
    IGuidanceDocument,
    IIndicator,
    IInformationPortal,
    IMapGraphDataset,
    IOrganisation,
    IPublicationReport,
    IResearchProject,
    ITool,
    IC3sIndicator,
)
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IPublicationReport, IClimateAdaptContent)
class PublicationReport(Container):
    search_type = "DOCUMENT"


@implementer(IInformationPortal, IClimateAdaptContent)
class InformationPortal(Container):
    search_type = "INFORMATIONSOURCE"


@implementer(IGuidanceDocument, IClimateAdaptContent)
class GuidanceDocument(Container):
    search_type = "GUIDANCE"


@implementer(ITool, IClimateAdaptContent)
class Tool(Container):
    search_type = "TOOL"


@implementer(IOrganisation, IClimateAdaptContent)
class Organisation(Container):
    search_type = "ORGANISATION"


@implementer(IIndicator, IClimateAdaptContent)
class Indicator(Container):
    search_type = "INDICATOR"


@implementer(IIndicator, IC3sIndicator, IClimateAdaptContent)
class C3sIndicator(Container):
    search_type = "INDICATOR"


@implementer(IMapGraphDataset, IClimateAdaptContent)
class MapGraphDataset(Container):
    search_type = "MAPGRAPHDATASET"


@implementer(IResearchProject, IClimateAdaptContent)
class ResearchProject(Container):
    search_type = "RESEARCHPROJECT"


@implementer(IAction, IClimateAdaptContent)
class Action(Container):
    search_type = "ACTION"
