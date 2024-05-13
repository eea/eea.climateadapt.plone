from eea.climateadapt.behaviors import IMainEvent
from plone.directives import dexterity
from zope.interface import implements

class MainEvent(dexterity.Container):
    implements(IMainEvent)