import json

from pkg_resources import resource_filename
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from zope.interface import provider
from zope.schema import URI

from eea.climateadapt import CcaAdminMessageFactory as _

fpath = resource_filename("eea.climateadapt.behaviors",
                          "volto_layout_news.json")
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

    remoteUrl = URI(
        title=_("Weblink for further reading"),
        required=False,
    )
