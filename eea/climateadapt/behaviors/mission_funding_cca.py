import json

from pkg_resources import resource_filename
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from plone.supermodel import model
from zope.interface import alsoProvides, provider
from zope.schema import Bool, Choice, List as ListField, TextLine
from plone.app.textfield import RichText

from eea.climateadapt import CcaAdminMessageFactory as _


fpath = resource_filename(
    "eea.climateadapt.behaviors", "volto_layout_missionfunding.json"
)
layout = json.load(open(fpath))


@provider(IFormFieldProvider)
class IMissionFundingCCA(model.Schema, IBlocks):
    """MissionFundingCCA Interface"""

    # Name of the funding programme (C) = title

    # form.fieldset(
    #     "mission_funding_metadata",
    #     label="Metadata",
    #     fields=[
    #         "country",
    #         # "regions",
    #         "rast_steps",
    #         "eligible_entities",
    #         "sectors",
    #     ],
    # )

    funding_type = ListField(
        title=_("Type of funding"),
        required=False,
        value_type=Choice(
            title=str("Type of funding"),
            vocabulary="eea.climateadapt.mission.type_of_funding",
        ),
        # column: Which type of funding is granted?
    )

    budget_range = ListField(
        title=_("Expected budget range of proposals"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.mission.budget_range",
        ),
        # column: What is the expected budget range of proposals?
    )

    is_blended = Bool(
        title=_(
            "Can the received funding be combined with other funding sources (blended)?"
        ),
        required=False,
        default=False,
        # column: Can the received funding be combined with other funding sources (blended)?
    )

    is_consortium_required = Bool(
        title=_("Is a Consortium required to apply for the funding?"),
        required=False,
        default=False,
        # column: Is a Consortium required to apply for the funding?
    )

    directives.widget(rast_steps="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    rast_steps = ListField(
        title=_("RAST step(s) of relevance"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.rast_steps",
        ),
        # metacolumn: For which step of the AST can the funding be used?
    )

    directives.widget(eligible_entities="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    eligible_entities = ListField(
        title=_("Eligible to receive funding"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.eligible_entities",
        ),
        # metacolumn: Who is eligible to receive funding?
    )

    directives.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = ListField(
        title=_("Adaptation Sectors"),
        description=_(
            "Select one or more relevant sector policies that this item relates to."
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
        # metacolumn: Which sectors can receive funding?
    )

    country = ListField(
        title=_("Countries where the funding opportunity is offered"),
        required=False,
        # TODO: disabled for plone6 migration
        # value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
        value_type=TextLine(title="Country"),
        #
        # column: For which country is this funding opportunity offered?
        # TODO: need manual intervention
    )

    # column: For which regions is the funding opportunity offered?
    regions = RichText(title=_("Region where the funding is offered"), required=False)

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

    # objective = RichText(
    #     title=_("Objective of the funding programme"),
    #     required=False,
    #     # column: Summarise the objective of the programme (headline format max 300c including spaces)
    # )
    #
    # funding_rate = TextLine(
    #     title=_("Funding rate (percentage of covered costs)"),
    #     required=False,
    #     # column: How high is the funding rate? (percentage of covered costs)
    # )
    #
    # column: Which authority administers the funding programme?
    # authority = TextLine(title=_("Administering authority"), required=False)
    #
    # publication_page = URI(
    #     title=_("Publication page"),
    #     required=False,
    #     # column: Please provide a link to the publication page of the individual calls.
    # )
    #
    # general_info = URI(
    #     title=_("General information"),
    #     required=False,
    #     # column: Provide a link to general information on the funding programme:
    # )
    #
    # Please provide a link to additional useful information
    # further_info = RichText(title=_("Further information"), required=False)
    #


alsoProvides(IMissionFundingCCA["sectors"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["country"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_blended"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_consortium_required"], ILanguageIndependentField)
# alsoProvides(IMissionFundingCCA["publication_page"], ILanguageIndependentField)
# alsoProvides(IMissionFundingCCA["general_info"], ILanguageIndependentField)
# alsoProvides(IMissionFundingCCA["regions"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["rast_steps"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["eligible_entities"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_consortium_required"], ILanguageIndependentField)
