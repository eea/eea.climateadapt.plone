from eea.climateadapt.behaviors import IMissionTool
from plone.directives import dexterity
from zope.interface import implements


class MissionTool(dexterity.Container):
    implements(IMissionTool)
