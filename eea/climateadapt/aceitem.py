from eea.climateadapt.behaviors import (IAction,
                                        IGuidanceDocument, IIndicator,
                                        IInformationPortal, IMapGraphDataset,
                                        IOrganisation, IPublicationReport,
                                        IResearchProject, ITool)
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity
from zope.interface import implementer


@implementer(IPublicationReport, IClimateAdaptContent)
class PublicationReport(dexterity.Container):
    search_type = "DOCUMENT"


@implementer(IInformationPortal, IClimateAdaptContent)
class InformationPortal(dexterity.Container):
    search_type = "INFORMATIONSOURCE"


@implementer(IGuidanceDocument, IClimateAdaptContent)
class GuidanceDocument(dexterity.Container):
    search_type = "GUIDANCE"


@implementer(ITool, IClimateAdaptContent)
class Tool(dexterity.Container):
    search_type = "TOOL"


@implementer(IOrganisation, IClimateAdaptContent)
class Organisation(dexterity.Container):
    search_type = "ORGANISATION"


@implementer(IIndicator, IClimateAdaptContent)
class Indicator(dexterity.Container):
    search_type = "INDICATOR"


@implementer(IIndicator, IClimateAdaptContent)
class C3sIndicator(dexterity.Container):
    search_type = "INDICATOR"


@implementer(IMapGraphDataset, IClimateAdaptContent)
class MapGraphDataset(dexterity.Container):
    search_type = "MAPGRAPHDATASET"


@implementer(IResearchProject, IClimateAdaptContent)
class ResearchProject(dexterity.Container):
    search_type = "RESEARCHPROJECT"


@implementer(IAction, IClimateAdaptContent)
class Action(dexterity.Container):
    search_type = "ACTION"
