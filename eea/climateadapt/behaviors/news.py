import json

from pkg_resources import resource_filename
from eea.climateadapt import CcaAdminMessageFactory as _
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import provider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField


fpath = resource_filename(
    "eea.climateadapt.behaviors", "volto_layout_news.json"
)
layout = json.load(open(fpath))


@provider(IFormFieldProvider)
class IMainNews(IBlocks):

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=layout["blocks"],
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default=layout["blocks_layout"],
        required=False,
    )
