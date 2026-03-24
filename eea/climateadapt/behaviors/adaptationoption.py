from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.relationfield.schema import RelationChoice, RelationList
from z3c.form.interfaces import IAddForm, IEditForm
from zope.interface import alsoProvides
from zope.schema import Choice, Date, List, Bool, TextLine, Text

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from .volto_layout import adaptation_option_layout_blocks, adaptation_option_layout_items


class IAdaptationOption(IAceMeasure, IBlocks):
    """Adaptation Option"""

    directives.omitted(IEditForm, "logo")
    directives.omitted(IAddForm, "logo")

    directives.omitted(IEditForm, "geochars")
    directives.omitted(IAddForm, "geochars")

    title = TextLine(
        title=_(u"Title"),
        description=_(
            u"Name of the adaptation option."
        ),
        max_length=250,
        required=True,
    )

    description = Text(
        title=_("Short summary"),
        required=False,
        description=_(
            "Summarize in one or two sentences the main purpose of the option or its main mechanism. "
            "This summary will be highlighted on the top of the page and used in listings "
            "(250 character limit)."
        ),
        missing_value="",
        max_length=250,
    )

    directives.widget(
        key_type_measures="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    key_type_measures = List(
        title=_("Key Type Measures"),
        description=_("Select Key Type Measures. The options are:"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_key_type_measures",
        ),
    )

    directives.widget(
        ipcc_category="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    ipcc_category = List(
        title=_("IPCC adaptation options categories"),
        description=_(
            "Select one or more categories of adaptation options. The options are:"
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_ipcc_category",
        ),
    )

    casestudies = RelationList(
        title=_("Case studies implemented in the adaption"),
        default=[],
        description=_(
            "Select one or more case study that this item relates to:"),
        value_type=RelationChoice(
            title=_("Related"),
            vocabulary="eea.climateadapt.case_studies",
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    publication_date = Date(
        title=_("Date of item's creation"),
        description=_(
            "The date refers to the moment in which the item "
            "has been prepared or  updated by contributing "
            "experts to be submitted for the publication in "
            "Climate ADAPT."
            " Please use the Calendar icon to add day/month/year. If you want to "
            'add only the year, please select "day: 1", "month: January" '
            "and then the year."
        ),
        required=True,
    )

    # dexteritytextindexer.searchable("source")
    source = RichText(
        title=_("References"),
        required=False,
        description=_(
            "Describe the references (projects, a tools reports, etc.) "
            "related to this item, providing further information about "
            "it or its source."
        ),
    )

    intro_paragraph = RichText(
        title=_("Introduction"),
        description=_("Provide an introductory paragraph for this adaptation option (1000 character limit)."),
        required=False,
        max_length=1000,
    )

    directives.widget(
        relevant_eu_policies="z3c.form.browser.checkbox.CheckBoxFieldWidget"
    )
    relevant_eu_policies = List(
        title=_("Relevant EU policies"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.relevant_eu_policies"),
    )

    advantages = RichText(
        title=_("Advantages"),
        description=_("Describe the advantages of this adaptation option (500 character limit)."),
        required=False,
        max_length=500,
    )

    disadvantages = RichText(
        title=_("Disadvantages"),
        description=_("Describe the disadvantages of this adaptation option (500 character limit)."),
        required=False,
        max_length=500,
    )

    directives.widget(
        relevant_synergies="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    relevant_synergies = List(
        title=_("Relevant synergies with mitigation"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.relevant_synergies",
        ),
    )

    show_related_resources = Bool(
        title=_("Show Related Resources"),
        description=_(
            "If selected, the tabs with 'Related resources' will be shown in the "
            "view of the item."
        ),
        required=False, 
        default=True
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=adaptation_option_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": adaptation_option_layout_items,
        },
        required=False,
    )

alsoProvides(IAdaptationOption["publication_date"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["casestudies"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["ipcc_category"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["key_type_measures"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["intro_paragraph"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["advantages"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["disadvantages"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["relevant_synergies"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["source"], ILanguageIndependentField)
alsoProvides(IAdaptationOption["show_related_resources"], ILanguageIndependentField)

