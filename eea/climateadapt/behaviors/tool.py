from zope.schema import Bool, Choice, List, TextLine, Int
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from .volto_layout import tool_layout_blocks, tool_layout_items
from zope.schema import Bool


class ITool(IAceItem, IBlocks):
    """Tool Interface"""

    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")

    # source = TextLine(title=_(u"Organisation's source"),
    #                  required=False,
    #                  description=u"Describe the original source of the item "
    #                              u"description (250 character limit)")

    include_in_navigator = Bool(
        title=_("Include in navigator"), required=False, default=False
    )

    directives.widget(
        type_of_outputs="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    type_of_outputs = List(
        title=_("Type of outputs"),
        description=_("Select one or more type of outputs."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.type_of_outputs_tool",
        ),
    )

    directives.widget(
        temporality_of_data="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    temporality_of_data = List(
        title=_("Temporality of data"),
        description=_("Select one or more temporality of data."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.temporality_of_data_tool",
        ),
    )

    directives.widget(
        accessibility_and_usability="z3c.form.browser.radio.RadioFieldWidget")
    accessibility_and_usability = Choice(
        title=_("Accessibility and usability"),
        description=_("Select one or more accessibility and usability."),
        required=False,
        vocabulary="eea.climateadapt.accessibility_and_usability_tool",
    )

    nature_based_solution = Bool(
        title=_("Nature-based solution"), required=False, default=False
    )

    just_resilience = Bool(title=_("Just resilience"),
                           required=False, default=False)

    cost_benefit_ratio = Bool(
        title=_("Cost-benefit ratio"), required=False, default=False
    )

    spatial_resolution = TextLine(
        title=_("Spatial resolution"),
        required=False,
        default=str(""),
        description=_("Free text (Local, NUTS3, NUTS2 ...)"),
    )

    underlying_data_maintenance = TextLine(
        title=_("Underlying data maintenance"),
        required=False,
        default=str(""),
    )

    functionality = Int(
        title="Functionality",
        required=False,
        description=_("Number of adaptation support cycle steps."),
    )

    strengths_and_possible_limitations = TextLine(
        title=_("Strengths and possible limitations of the tool"),
        required=False,
        default=str(""),
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=tool_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={"items": tool_layout_items},
        required=False,
    )
