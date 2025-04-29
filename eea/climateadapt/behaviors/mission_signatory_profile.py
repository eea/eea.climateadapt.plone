# import json

# from pkg_resources import resource_filename

from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.behaviors import IBlocks  # BLOCKS_SCHEMA, LAYOUT_SCHEMA,
from plone.supermodel import model
from zope.interface import provider


# from eea.climateadapt import CcaAdminMessageFactory as _

# fpath = resource_filename(
#     "eea.climateadapt.behaviors", "volto_layout_missionfunding.json"
# )
# layout = json.load(open(fpath))


@provider(IFormFieldProvider)
class IMissionSignatoryProfile(model.Schema, IBlocks):
    """IMissionSignatoryProfile Interface"""

    # blocks = JSONField(
    #     title=_("Blocks"),
    #     description=_("The JSON representation of the object blocks."),
    #     schema=BLOCKS_SCHEMA,
    #     default=layout["blocks"],
    #     required=False,
    # )

    # blocks_layout = JSONField(
    #     title=_("Blocks Layout"),
    #     description=_("The JSON representation of the object blocks layout."),
    #     schema=LAYOUT_SCHEMA,
    #     default=layout["blocks_layout"],
    #     required=False,
    # )
