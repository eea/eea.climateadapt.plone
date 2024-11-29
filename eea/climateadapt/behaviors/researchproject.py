# from eea.climateadapt import CcaAdminMessageFactory as _
# from eea.climateadapt.behaviors.aceitem import IAceItem
# from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA
# from plone.schema import JSONField
# from .volto_layout import research_layout_blocks, research_layout_items


# class IResearchProject(IAceItem):
#     """ResearchProject Interface"""

#     blocks = JSONField(
#         title=_("Blocks"),
#         description=_("The JSON representation of the object blocks."),
#         schema=BLOCKS_SCHEMA,
#         default=research_layout_blocks,
#         required=False,
#     )

#     blocks_layout = JSONField(
#         title=_("Blocks Layout"),
#         description=_("The JSON representation of the object blocks layout."),
#         schema=LAYOUT_SCHEMA,
#         default={
#             "items": research_layout_items
#         },
#         required=False,
#     )
