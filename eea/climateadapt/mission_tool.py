from eea.climateadapt.behaviors import IMissionTool
from plone.directives import dexterity
from zope.interface import implementer


@implementer(IMissionTool)
class MissionTool(dexterity.Container):
