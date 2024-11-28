from zope.interface import implementer

from eea.climateadapt.behaviors import IAceVideo
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity


@implementer(IAceVideo, IClimateAdaptContent)
class Video(dexterity.Container):
    """A video content type implementation"""

    search_type = "VIDEO"
