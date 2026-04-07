from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.form.interfaces import IAddForm, IEditForm
from zope.interface import alsoProvides
from zope.schema import TextLine

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem

from .volto_layout import organisation_layout_blocks, organisation_layout_items

# from z3c.form.browser.textlines import TextLinesWidget


class IOrganisation(IAceItem, IBlocks):
    """Organisation Interface"""

    directives.omitted(IAddForm, "health_impacts")
    directives.omitted(IEditForm, "health_impacts")
    directives.omitted(IAddForm, "source")
    directives.omitted(IEditForm, "source")
    directives.omitted(IEditForm, "contributor_list")
    directives.omitted(IAddForm, "contributor_list")
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")

    acronym = TextLine(
        title=_("Acronym"),
        description=_("Acronym of the organisation"),
        required=False,
    )

    contact = TextLine(
        title=_("Contact"),
        description=_("Corporate email or link to contact form"),
        required=False,  # TODO set to True after plone6 migration
    )

    title = TextLine(
        title=_("Name"), description="Item Name (250 character limit)", required=True
    )

    organisational_key_activities = RichText(
        title=_(
            "Key activities within climate change and health (relevant for the Observatory)"
        ),
        description="Please describe the key activities"
        " undertaken by your organisation that are related"
        " to the topic of 'climate change and health'."
        " Please concentrate on activities with most"
        " direct relevance to the Observatory. You may"
        " include any hyperlinks to relevant projects in"
        " the text",
        required=False,
    )

    # directives.widget("organisational_links", TextLinesWidget)

    organisational_websites = RichText(
        title=_("Links to further information (relevant for the Observatory)"),
        description="Please provide a hyperlink to the homepage"
        ' of your organisation in the "Reference'
        ' Information section", here you may also'
        " provide links to up to two relevant units of"
        " the organisation that have directly contributed"
        " to the Observatory and/or up to two hyperlinks"
        " to relevant networks (e.g. with countries) that"
        " are administered by your organisation",
        required=False,
    )

    organisational_contact_information = RichText(
        title=_("Contact information for the Observatory"),
        description="Please provide a corporate email or contact"
        ' form link into the "Default section", here you'
        " may provide further contact information relevant"
        " for the organisation's contribution to the"
        " Observatory.",
        required=False,
    )

    # form.fieldset('default',
    #              label=u'Item Description',
    #         fields=['acronym', 'title', 'description', 'long_description',
    #                 'keywords', 'sectors', 'climate_impacts', 'elements',
    #                 ]
    #         )

    logo = NamedBlobImage(
        title=_("Logo"),
        description=_(
            "Upload a representative picture or logo for the item."
            " Recommended size: at least 360/180 px, aspect ratio 2x"
        ),
        required=False,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=organisation_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={"items": organisation_layout_items},
        required=False,
    )


alsoProvides(IOrganisation["acronym"], ILanguageIndependentField)
alsoProvides(IOrganisation["contact"], ILanguageIndependentField)
alsoProvides(IOrganisation["organisational_websites"], ILanguageIndependentField)
alsoProvides(
    IOrganisation["organisational_contact_information"], ILanguageIndependentField
)
# blobs are handled by field serializer
# alsoProvides(IOrganisation["logo"], ILanguageIndependentField)
