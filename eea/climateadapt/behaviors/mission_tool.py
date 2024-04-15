from eea.climateadapt import CcaAdminMessageFactory as _
from zope.schema import Choice, List
from plone.directives import form
from plone.restapi.behaviors import IBlocks
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from zope.interface import alsoProvides, provider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
# from .volto_layout import mission_funding_cca_layout_blocks, mission_funding_cca_layout_items

from plone.app.textfield import RichText


@provider(IFormFieldProvider)
class IMissionTool(model.Schema, IBlocks):
    """MissionTool Interface"""

    form.fieldset(
        "mission_tool_metadata",
        label="Metadata",
        fields = [
            "objective",
            "short_description",
            "free_keywords",
            "readiness_for_use",
            "applications",
            "strengths_weaknesses",
            "rast_steps",
            "input",
            "output",
            "geographical_scale",
            "geographical_area",
            "climate_impacts",
            "tool_language",
            "sectors",
            "most_useful_for",
            "user_requirements",
            "replicability",
            "materials",
            "website",
            "contact",
            "associated_project",
        ]
    )

    objective = RichText(
        title=_("Objective(s)"),
        required=False,
    )

    short_description = RichText(
        title=_("Short description"),
        required=False,
    )

    free_keywords = RichText(
        title=_("Free keywords"),
        required=False,
    )

    form.widget(readiness_for_use="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    readiness_for_use = List(
        title=_("Readiness for use"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.readiness_for_use",
        ),
    )

    applications = RichText(
        title=_("Applications"),
        required=False,
    )

    strengths_weaknesses = RichText(
        title=_("Strengths and weaknesses, comparative added value to other similar tools"),
        required=False,
    )

    form.widget(rast_steps="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    rast_steps = List(
        title=_("RAST step(s) of relevance"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.rast_steps",
        ),
    )

    input = RichText(
        title=_("Input(s)"),
        required=False,
    )

    output = RichText(
        title=_("Output(s)"),
        required=False,
    )

    form.widget(geographical_scale="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    geographical_scale = List(
        title=_("Geographical scale"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.geographical_scale",
        ),
    )

    geographical_area = RichText(
        title=_("Geographical area"),
        required=False
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate Impacts"),
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    form.widget(tool_language="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    tool_language = List(
        title=_("Language(s) of the tool"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.tool_language",
        ),
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Adaptation Sectors"),
        description=_(
            "Select one or more relevant sector policies that " "this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    form.widget(most_useful_for="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    most_useful_for = List(
        title=_("Most useful for"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.most_useful_for",
        ),
    )

    form.widget(user_requirements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    user_requirements = List(
        title=_("User requirements"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.user_requirements",
        ),
    )

    replicability = RichText(
        title=_("Replicability: Cost/effort for (new) usage"),
        required=False
    )

    materials = RichText(
        title=_("Materials or other support available"),
        required=False
    )

    website = RichText(
        title=_("Website and maintenance"),
        required=False
    )

    contact = RichText(
        title=_("Contact"),
        required=False
    )

    associated_project = RichText(
        title=_("Associated project(s)"),
        required=False
    )

    # blocks = JSONField(
    #     title=_("Blocks"),
    #     description=_("The JSON representation of the object blocks."),
    #     schema=BLOCKS_SCHEMA,
    #     default=mission_funding_cca_layout_blocks,
    #     required=False,
    # )

    # blocks_layout = JSONField(
    #     title=_("Blocks Layout"),
    #     description=_("The JSON representation of the object blocks layout."),
    #     schema=LAYOUT_SCHEMA,
    #     default={
    #         "items": mission_funding_cca_layout_items,
    #     },
    #     required=False,
    # )

alsoProvides(IMissionTool['objective'], ILanguageIndependentField)
alsoProvides(IMissionTool['short_description'], ILanguageIndependentField)
alsoProvides(IMissionTool['free_keywords'], ILanguageIndependentField)
alsoProvides(IMissionTool['readiness_for_use'], ILanguageIndependentField)
alsoProvides(IMissionTool['applications'], ILanguageIndependentField)
alsoProvides(IMissionTool['strengths_weaknesses'], ILanguageIndependentField)
alsoProvides(IMissionTool['rast_steps'], ILanguageIndependentField)
alsoProvides(IMissionTool['input'], ILanguageIndependentField)
alsoProvides(IMissionTool['output'], ILanguageIndependentField)
alsoProvides(IMissionTool['geographical_scale'], ILanguageIndependentField)
alsoProvides(IMissionTool['geographical_area'], ILanguageIndependentField)
alsoProvides(IMissionTool['climate_impacts'], ILanguageIndependentField)
alsoProvides(IMissionTool['tool_language'], ILanguageIndependentField)
alsoProvides(IMissionTool['sectors'], ILanguageIndependentField)
alsoProvides(IMissionTool['most_useful_for'], ILanguageIndependentField)
alsoProvides(IMissionTool['user_requirements'], ILanguageIndependentField)
alsoProvides(IMissionTool['replicability'], ILanguageIndependentField)
alsoProvides(IMissionTool['materials'], ILanguageIndependentField)
alsoProvides(IMissionTool['website'], ILanguageIndependentField)
alsoProvides(IMissionTool['contact'], ILanguageIndependentField)
alsoProvides(IMissionTool['associated_project'], ILanguageIndependentField)
