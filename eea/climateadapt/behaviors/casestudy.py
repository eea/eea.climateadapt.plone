from plone.app.contenttypes.interfaces import IImage
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobImage
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.form.interfaces import IAddForm, IEditForm
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides
from zope.schema import Choice, List, TextLine, Tuple

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from .volto_layout import case_study_layout_blocks, case_study_layout_items


class ICaseStudy(IAceMeasure, IBlocks):  # , IGeolocatable):
    """Case study"""

    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")
    directives.omitted(IEditForm, "primephoto")
    directives.omitted(IAddForm, "primephoto")
    directives.omitted(IEditForm, "supphotos")
    directives.omitted(IAddForm, "supphotos")

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'relatedItems')
    # directives.omitted(IAddForm, 'relatedItems')

    directives.widget("updating_notes", vocabulary="updating_notes_vocabulary")
    updating_notes = Tuple(
        title=_("Updating notes"),
        required=False,
        default=(),
        missing_value=None,
        value_type=TextLine(
            title=_("Single topic"),
        ),
    )

    policy_legal_background = RichText(
        title=_("Policy and legal background"),
        required=False,
        default=None,
    )

    challenges = RichText(
        title=_("Challenges"),
        required=True,
        default=None,
        description=_(
            "Describe what are the main climate change "
            "impacts/risks and related challenges addressed by the "
            "adaptation solutions proposed by the case study. "
            "Possibly include quantitate scenarios/projections of "
            "future climate change considered by the case study "
            "(5,000 characters limit):"
        ),
    )

    objectives = RichText(
        title=_("Objectives of the adaptation measure"),
        required=True,
        default=None,
        description=_(
            "Describe the objectives which triggered the "
            "adaptation measures (5,000 characters limit):"
        ),
    )

    solutions = RichText(
        title=_("Solutions"),
        required=True,
        default=None,
        description=_(
            "Describe the climate change adaptation solution(s) "
            "implemented (5,000 characters limit):"
        ),
    )

    form.widget(relevance="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    relevance = List(
        title=_("Relevance"),
        required=True,
        missing_value=[],
        default=None,
        description=_(
            "Select only one category below that best describes "
            "how relevant this case study is to climate change "
            "adaptation:"
        ),
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_relevance",
        ),
    )

    contact = RichText(
        title=_("Contact"),
        required=True,
        default=str(""),
        description=_(
            "Contact of reference (institution and persons) who is "
            "directly involved in the development and "
            "implementation of the case. (500 char limit) "
        ),
    )

    adaptationoptions = RelationList(
        title=_("Adaptation measures implemented in the case:"),
        default=[],
        description=_(
            "Select one or more adaptation options that this item " "relates to:"
        ),
        value_type=RelationChoice(
            title=_("Related"),
            vocabulary="eea.climateadapt.adaptation_options",
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    primary_photo = NamedBlobImage(
        title=_("Primary photo"),
        required=False,
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

    primary_photo_copyright = TextLine(
        title=_("Primary Photo Copyright"),
        required=False,
        default=str(""),
        description=_(
            "Copyright statement or other rights information for  " "the primary photo."
        ),
    )

    form.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation approaches"),
        description=_("Select one or more approaches."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements_case_study",
        ),
    )

    # BBB fields, only used during migration
    primephoto = RelationChoice(
        title=_("Prime photo"),
        source=ObjPathSourceBinder(object_provides=IImage.__identifier__),
        required=False,
    )
    supphotos = RelationList(
        title=_("Gallery"),
        default=[],
        value_type=RelationChoice(
            title=_("Related"),
            source=ObjPathSourceBinder(object_provides=IImage.__identifier__),
        ),
        required=False,
    )

    # form.fieldset(
    #     "default",
    #     label=u"Item Description",
    #     fields=[
    #         "updating_notes",
    #         "primary_photo",
    #         "primary_photo_copyright",
    #         "challenges",
    #         "policy_legal_background",
    #         "relevance",
    #         "objectives",
    #         "adaptationoptions",
    #         "solutions",
    #         # "keywords",
    #         # "sectors",
    #         # "elements",
    #         # 'origin_website',
    #         # 'logo',
    #         # 'image',
    #         # 'contributor_list',
    #         # 'other_contributor',
    #         # "featured",  # 'year',
    #     ],
    # )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=case_study_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={"items": case_study_layout_items},
        required=False,
    )


alsoProvides(ICaseStudy["relevance"], ILanguageIndependentField)
alsoProvides(ICaseStudy["contact"], ILanguageIndependentField)
alsoProvides(ICaseStudy["adaptationoptions"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primary_photo"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primary_photo_copyright"], ILanguageIndependentField)
alsoProvides(ICaseStudy["primephoto"], ILanguageIndependentField)
alsoProvides(ICaseStudy["supphotos"], ILanguageIndependentField)
