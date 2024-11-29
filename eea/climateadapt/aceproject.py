from zope.interface import implementer

from eea.climateadapt.behaviors import IAceProject
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.dexterity.content import Container

@implementer(IAceProject, IClimateAdaptContent)
class AceProject(Container):

    search_type = "RESEARCHPROJECT"
