from eea.climateadapt.behaviors import IMissionFundingCCA
from plone.directives import dexterity
from zope.interface import implements


class MissionFundingCCA(dexterity.Container):
    implements(IMissionFundingCCA)
