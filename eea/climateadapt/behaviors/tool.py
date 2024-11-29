# from eea.climateadapt import CcaAdminMessageFactory as _
# from eea.climateadapt.behaviors.aceitem import IAceItem
# from plone.autoform import directives
# from z3c.form.interfaces import IAddForm, IEditForm
# from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
# from plone.schema import JSONField
# from .volto_layout import tool_layout_blocks, tool_layout_items

# class ITool(IAceItem, IBlocks):
#     """Tool Interface"""

#     # directives.omitted(IAddForm, 'year')
#     # directives.omitted(IEditForm, 'year')
#     directives.omitted(IEditForm, "featured")
#     directives.omitted(IAddForm, "featured")

#     # source = TextLine(title=_(u"Organisation's source"),
#     #                  required=False,
#     #                  description=u"Describe the original source of the item "
#     #                              u"description (250 character limit)")

#     blocks = JSONField(
#         title=_("Blocks"),
#         description=_("The JSON representation of the object blocks."),
#         schema=BLOCKS_SCHEMA,
#         default=tool_layout_blocks,
#         required=False,
#     )

#     blocks_layout = JSONField(
#         title=_("Blocks Layout"),
#         description=_("The JSON representation of the object blocks layout."),
#         schema=LAYOUT_SCHEMA,
#         default={
#             "items": tool_layout_items
#         },
#         required=False,
#     )
