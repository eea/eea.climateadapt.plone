from .aceitem import IAceItem
from .volto_layout import video_layout_blocks, video_layout_items
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from zope.interface import alsoProvides
from zope.schema import TextLine, Date


class IAceVideo(IAceItem, IBlocks):
    """Video schema"""

    embed_url = TextLine(
        title=_("Video URL"), description="Enter the video URL", required=True
    )

    video_height = TextLine(
        title=_("Video Height"),
        description="Enter the video height",
        required=False,
        default="480",
    )

    publication_date = Date(
        title=_("Date of video's release"),
        description="The date refers to the moment in which the video has "
        "been released. Please use the Calendar icon to add day/month/year. "
        "If you want to add only the year, please select \"day: 1\", "
        "\"month: January\" and then the year",
        required=True,
    )

    related_documents_presentations = RichText(
        title=_("Related documents and presentations"),
        required=False,
        default=None
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=video_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": video_layout_items
        },
        required=False,
    )

alsoProvides(IAceVideo["embed_url"], ILanguageIndependentField)
alsoProvides(IAceVideo["video_height"], ILanguageIndependentField)
alsoProvides(IAceVideo["publication_date"], ILanguageIndependentField)
alsoProvides(IAceVideo["related_documents_presentations"], ILanguageIndependentField)
