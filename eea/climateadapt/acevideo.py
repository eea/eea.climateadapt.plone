from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.directives import dexterity
from zope.schema import TextLine
from .aceitem import IAceItem
from zope.interface import implements


class IAceVideos(IAceItem):
    youtube_url = TextLine(title=_(u"Video URL"),
                           description=u"Enter the video URL from youtube",
                           required=True)

    video_height = TextLine(title=_(u"Video Height"),
                            description=u"Enter the video height",
                            required=False,
                            default=u"480")


class Videos(dexterity.Container):
    implements(IAceVideos, IClimateAdaptContent)

    search_type = "VIDEOS"
