from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides
from zope.schema import Choice, Date, List, Bool

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from .volto_layout import adaptation_option_layout_blocks, adaptation_option_layout_items


class IAdaptationOption(IAceMeasure, IBlocks):
    """Adaptation Option"""

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
            "and then the year"
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
        required=False,
    )

    advantages = RichText(
        title=_("Advantages"),
        required=False,
    )

    disadvantages = RichText(
        title=_("Disadvantages"),
        required=False,
    )

    relevant_synergies = Choice(
        title=_("Relevant synergies with mitigation"),
        required=False,
        vocabulary="eea.climateadapt.relevant_synergies",
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

