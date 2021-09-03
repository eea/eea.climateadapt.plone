from zope.schema import Text, TextLine, Date

from eea.climateadapt import MessageFactory as _

from .aceitem import IAceItem
from plone.app.textfield import RichText


class IAceVideo(IAceItem):
    """Video schema"""

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
        title=_(u"Date of video's release"),
        description=u"The date refers to the moment in which the video has "
        u"been released. Please use the Calendar icon to add day/month/year. "
        u"If you want to add only the year, please select \"day: 1\", "
        u"\"month: January\" and then the year",
        required=True,
    )

    related_documents_presentations = RichText(
        title=_(u"Related documents and presentations"),
        required=False,
        default=None
    )
