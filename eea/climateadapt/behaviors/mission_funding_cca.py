from eea.climateadapt import CcaAdminMessageFactory as _
from zope.schema import Choice, List, TextLine, Bool, URI
from plone.directives import form
from plone.restapi.behaviors import IBlocks
from plone.supermodel import model
from plone.autoform.interfaces import IFormFieldProvider
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from zope.interface import alsoProvides, provider
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from .volto_layout import mission_funding_cca_layout_blocks, mission_funding_cca_layout_items

from plone.app.textfield import RichText


@provider(IFormFieldProvider)
class IMissionFundingCCA(model.Schema, IBlocks):
    """MissionFundingCCA Interface"""

    form.fieldset(
        "mission_funding_metadata",
        label="Metadata",
        fields=[
            "country",
            "regions",
            "rast_steps",
            "eligible_entities",
            "sectors",
        ],
    )

    objective = RichText(
        title=_("Objective of the funding programme"),
        required=False,
    )

    funding_type = RichText(
        title=_("Type of funding"),
        required=False,
    )

    budget_range = TextLine(
        title=_("Expected budget range of proposals"), required=False
    )
    funding_rate = TextLine(
        title=_("Funding rate (percentage of covered costs)"), required=False
    )

    is_blended = Bool(
        title=_(
            "Can the received funding be combined with other funding sources (blended)?"
        ),
        required=False,
        default=False,
    )

    is_consortium_required = Bool(
        title=_("Is a Consortium required to apply for the funding?"),
        required=False,
        default=False,
    )
    authority = TextLine(title=_("Administering authority"), required=False)

    publication_page = URI(
        title=_("Publication page"),
        required=False,
    )

    general_info = URI(
        title=_("General information"),
        required=False,
    )

    further_info = TextLine(title=_("Further information"), required=False)
    regions = TextLine(title=_("Region where the funding is offered"), required=False)

    form.widget(rast_steps="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    rast_steps = List(
        title=_("RAST step(s) of relevance"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.rast_steps",
        ),
    )

    form.widget(eligible_entities="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    eligible_entities = List(
        title=_("Eligible to receive funding"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.eligible_entities",
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

    country = List(
        title=_("Countries where the funding opportunity is offered"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=mission_funding_cca_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": mission_funding_cca_layout_items,
        },
        required=False,
    )

alsoProvides(IMissionFundingCCA["sectors"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["country"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_blended"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_consortium_required"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["publication_page"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["general_info"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["regions"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["rast_steps"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["eligible_entities"], ILanguageIndependentField)
alsoProvides(IMissionFundingCCA["is_consortium_required"], ILanguageIndependentField)
