from eea.climateadapt.behaviors import (IAction,
                                        IGuidanceDocument, IIndicator,
                                        IInformationPortal, IMapGraphDataset,
                                        IOrganisation, IPublicationReport,
                                        IResearchProject, ITool)
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity
from zope.interface import implements


class PublicationReport(dexterity.Container):
    implements(IPublicationReport, IClimateAdaptContent)

    search_type = "DOCUMENT"


class InformationPortal(dexterity.Container):
    implements(IInformationPortal, IClimateAdaptContent)

    search_type = "INFORMATIONSOURCE"


class GuidanceDocument(dexterity.Container):
    implements(IGuidanceDocument, IClimateAdaptContent)

    search_type = "GUIDANCE"


class Tool(dexterity.Container):
    implements(ITool, IClimateAdaptContent)

    search_type = "TOOL"


class Organisation(dexterity.Container):
    implements(IOrganisation, IClimateAdaptContent)

    search_type = "ORGANISATION"


class Indicator(dexterity.Container):
    implements(IIndicator, IClimateAdaptContent)

    search_type = "INDICATOR"


class C3sIndicator(dexterity.Container):
    implements(IIndicator, IClimateAdaptContent)

    search_type = "INDICATOR"


class MapGraphDataset(dexterity.Container):
    implements(IMapGraphDataset, IClimateAdaptContent)

    search_type = "MAPGRAPHDATASET"


class ResearchProject(dexterity.Container):
    implements(IResearchProject, IClimateAdaptContent)

    search_type = "RESEARCHPROJECT"


class Action(dexterity.Container):
    implements(IAction, IClimateAdaptContent)

    search_type = "ACTION"
