from zope.schema import Bool, Choice, List, TextLine, Int
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from .volto_layout import tool_layout_blocks, tool_layout_items
from zope.schema import Bool


from .tool import ITool


class IExtendedTool(ITool, IBlocks):
    """ExtendedTool Interface"""

    directives.omitted(IAddForm, "external_id")
    directives.omitted(IEditForm, "external_id")
    external_id = TextLine(
        title=_("External ID"),
        required=False,
        default=str(""),
    )

    tool_provider = TextLine(
        title=_("Tool provider"),
        required=False,
        default=str(""),
    )

    include_in_navigator = Bool(
        title=_("Include in navigator"), required=False, default=False
    )

    directives.widget(type_of_outputs="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    type_of_outputs = List(
        title=_("Type of outputs"),
        description=_("Select one or more type of outputs."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.type_of_outputs_tool",
        ),
    )

    directives.widget(
        temporality_of_data="z3c.form.browser.checkbox.CheckBoxFieldWidget"
    )
    temporality_of_data = List(
        title=_("Temporality of data"),
        description=_("Select one or more temporality of data."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.temporality_of_data_tool",
        ),
    )

    directives.widget(
        accessibility_and_usability="z3c.form.browser.radio.RadioFieldWidget"
    )
    accessibility_and_usability = Choice(
        title=_("Accessibility and usability"),
        description=_("Select one or more accessibility and usability."),
        required=False,
        vocabulary="eea.climateadapt.accessibility_and_usability_tool",
    )
