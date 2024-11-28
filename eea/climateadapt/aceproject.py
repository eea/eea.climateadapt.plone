from zope.interface import implementer

from eea.climateadapt.behaviors import IAceProject
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity

@implementer(IAceProject, IClimateAdaptContent)
class AceProject(dexterity.Container):

    search_type = "RESEARCHPROJECT"
