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

    public_private_mode = TextLine(
        title=_("Public/private"),
        description=_("academi, public, Public–academic ..."),
        required=False,
    )

    contact = TextLine(
        title=_("Contact"),
        description=_("person / email"),
        required=False,
    )

    hyperlink = TextLine(
        title=_("Hyperlink"),
        description=_("Tool hyperlink"),
        required=False,
    )

    coder_1 = TextLine(
        title=_("CODER 1"),
        description=_("Code"),
        required=False,
    )

    coder_2 = TextLine(
        title=_("CODER 2"),
        description=_("Code"),
        required=False,
    )

    directives.widget(
        intended_user_groups="z3c.form.browser.checkbox.CheckBoxFieldWidget"
    )
    intended_user_groups = List(
        title=_("Intended User Groups"),
        description=_("Select one or more intended user groups."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.intended_user_groups_tool",
        ),
    )

    directives.widget(
        place_of_implementation="z3c.form.browser.checkbox.CheckBoxFieldWidget"
    )
    place_of_implementation = List(
        title=_("Place of implementation"),
        description=_("Select one or more place of implementation."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.place_of_implementation_tool",
        ),
    )

    directives.widget(type_of_data="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    type_of_data = List(
        title=_("Type of data"),
        description=_("Select one or more type of data."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.type_of_data_tool",
        ),
    )

    directives.widget(data_sources="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    data_sources = List(
        title=_("Data sources"),
        description=_("Select one or more data sources."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.data_sources_tool",
        ),
    )

    directives.widget(license_status="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    license_status = List(
        title=_("License status"),
        description=_("Select one or more license status."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.license_status_tool",
        ),
    )
    # Hazard - THIS IS ALREADY IN USE
    # User support provisions
    # Tool validation use
    # Number of users / uptake (if known)
    # Tool provider [private, public, both, other]
    # Sector - THIS IS ALREADY IN USE
    # Adaptation Support Cycle Step

    include_in_navigator = Bool(
        title=_("Include in navigator"), required=False, default=False
    )

    tool_available_english = Bool(
        title=_("Is tool available in English?"), required=False, default=False
    )
    tool_available_language = TextLine(
        title=_("Tool language"),
        description=_("In which language(s) is the tool available, if not English"),
        required=False,
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
