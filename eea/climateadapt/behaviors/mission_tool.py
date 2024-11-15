import json

from pkg_resources import resource_filename

from eea.climateadapt import CcaAdminMessageFactory as _
from zope.schema import Choice, List
from plone.directives import form
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from zope.interface import alsoProvides, provider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField

fpath = resource_filename(
    "eea.climateadapt.behaviors", "volto_layout_mission_tools.json"
)
layout = json.load(open(fpath))


@provider(IFormFieldProvider)
class IMissionTool(model.Schema, IBlocks):
    """MissionTool Interface"""

    # form.fieldset(
    #     "mission_tool_metadata",
    #     label="Metadata",
    #     fields = [
    #         "readiness_for_use",
    #         "rast_steps",
    #         "geographical_scale",
    #         "climate_impacts",
    #         "tool_language",
    #         "sectors",
    #         "most_useful_for",
    #         "user_requirements"
    #     ]
    # )

    form.widget(
        readiness_for_use="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    readiness_for_use = List(
        title=_("Readiness for use"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.readiness_for_use",
        ),
    )

    form.widget(rast_steps="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    rast_steps = List(
        title=_("RAST step(s) of relevance"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.rast_steps",
        ),
    )

    form.widget(
        geographical_scale="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    geographical_scale = List(
        title=_("Geographical scale"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.geographical_scale",
        ),
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_("Climate impacts"),
        description=_(
            "Select one or more climate change impact topics that "
            "this item relates to."
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
        title=_("Adaptation sectors"),
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

    form.widget(
        user_requirements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    user_requirements = List(
        title=_("User requirements"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.user_requirements",
        ),
    )

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


alsoProvides(IMissionTool["readiness_for_use"], ILanguageIndependentField)
alsoProvides(IMissionTool["rast_steps"], ILanguageIndependentField)
alsoProvides(IMissionTool["geographical_scale"], ILanguageIndependentField)
alsoProvides(IMissionTool["climate_impacts"], ILanguageIndependentField)
alsoProvides(IMissionTool["tool_language"], ILanguageIndependentField)
alsoProvides(IMissionTool["sectors"], ILanguageIndependentField)
alsoProvides(IMissionTool["most_useful_for"], ILanguageIndependentField)
alsoProvides(IMissionTool["user_requirements"], ILanguageIndependentField)
