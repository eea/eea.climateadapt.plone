from eea.climateadapt.behaviors import IMissionTool
from plone.dexterity.content import Container
from zope.interface import implementer


@implementer(IMissionTool)
class MissionTool(Container):
