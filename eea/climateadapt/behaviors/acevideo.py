from zope.schema import Text, TextLine, Date

from eea.climateadapt import MessageFactory as _

from .aceitem import IAceItem


class IAceVideo(IAceItem):
    """Video schema"""

    embed = Text(
        title=_(u"Video Embed code"),
        description=u"Optional, enter video embed HTML code",
        required=False,
    )

    embed_url = TextLine(
        title=_(u"Video URL"), description=u"Enter the video URL", required=True
    )

    video_height = TextLine(
        title=_(u"Video Height"),
        description=u"Enter the video height",
        required=False,
        default=u"480",
    )

    publication_date = Date(
        title=_(u"Date of item's creation"),
        description=u"The date refers to the moment in which the video has "
        u"been released. Please use the Calendar icon to add day/month/year. "
        u"If you want to add only the year, please select \"day: 1\", "
        u"\"month: January\" and then the year",
        required=True,
    )
