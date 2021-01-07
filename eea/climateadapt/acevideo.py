from zope.interface import implements

from eea.climateadapt.behaviors import IAceVideo
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity


class Video(dexterity.Container):
    """A video content type implementation"""

    implements(IAceVideo, IClimateAdaptContent)

    search_type = "VIDEO"
