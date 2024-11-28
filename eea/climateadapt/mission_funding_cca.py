from eea.climateadapt.behaviors import IMissionFundingCCA
from plone.directives import dexterity
from zope.interface import implementer


@implementer(IMissionFundingCCA)
class MissionFundingCCA(dexterity.Container):
