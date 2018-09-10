from zope.interface import implements
from zope.schema import Text, TextLine

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity

from .aceitem import IAceItem


class IAceVideo(IAceItem):
    """ Video schema
    """

    embed = Text(title=_(u"Video Embed code"),
                 description=u"Optional, enter video embed HTML code",
                 required=False)

    embed_url = TextLine(title=_(u"Video URL"),
                         description=u"Enter the video URL",
                         required=False)

    video_height = TextLine(title=_(u"Video Height"),
                            description=u"Enter the video height",
                            required=False,
                            default=u"480")


class Video(dexterity.Container):
    """ A video content type implementation
    """

    implements(IAceVideo, IClimateAdaptContent)

    search_type = "VIDEO"
