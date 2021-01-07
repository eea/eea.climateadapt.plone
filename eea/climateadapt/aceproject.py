from zope.interface import implements

from eea.climateadapt.behaviors import IAceProject
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity


class AceProject(dexterity.Container):
    implements(IAceProject, IClimateAdaptContent)

    search_type = "RESEARCHPROJECT"
