from zope.interface import implementer

from eea.climateadapt.behaviors import IAceVideo
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.dexterity.content import Container


@implementer(IAceVideo, IClimateAdaptContent)
class Video(Container):
    """A video content type implementation"""

    search_type = "VIDEO"
