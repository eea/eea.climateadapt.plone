from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm
from zope.interface import alsoProvides
from zope.schema import TextLine

from .volto_layout import organisation_layout_blocks, organisation_layout_items


class IOrganisation(IAceItem, IBlocks):
    """ Organisation Interface"""

    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    directives.omitted(IAddForm, "health_impacts")
    directives.omitted(IEditForm, "health_impacts")
    directives.omitted(IAddForm, "source")
    directives.omitted(IEditForm, "source")
    directives.omitted(IEditForm, "contributor_list")
    directives.omitted(IAddForm, "contributor_list")
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    acronym = TextLine(
        title=_(u"Acronym"),
        description=_(u"Acronym of the organisation"),
        required=False,
    )

    contact = TextLine(
        title=_(u"Contact"),
        description=_(u"Corporate email or link to contact form"),
        required=True,
    )

    title = TextLine(
        title=_(u"Name"), description=u"Item Name (250 character limit)", required=True
    )

    organisational_key_activities = RichText(
        title=_(u"Key activities within climate change and health (relevant for the Observatory)"),
        description=u"Please describe the key activities"
        u" undertaken by your organisation that are related"
        u" to the topic of 'climate change and health'."
        u" Please concentrate on activities with most"
        u" direct relevance to the Observatory. You may"
        u" include any hyperlinks to relevant projects in"
        u" the text",
        required=False,
    )

    directives.widget("organisational_links", TextLinesWidget)

    organisational_websites = RichText(
        title=_(u"Links to further information (relevant for the Observatory)"),
        description=u"Please provide a hyperlink to the homepage"
        u' of your organisation in the "Reference'
        u' Information section", here you may also'
        u" provide links to up to two relevant units of"
        u" the organisation that have directly contributed"
        u" to the Observatory and/or up to two hyperlinks"
        u" to relevant networks (e.g. with countries) that"
        u" are administered by your organisation",
        required=False,
    )

    organisational_contact_information = RichText(
        title=_(u"Contact information for the Observatory"),
        description=u"Please provide a corporate email or contact"
        u' form link into the "Default section", here you'
        u" may provide further contact information relevant"
        u" for the organisation's contribution to the"
        u" Observatory.",
        required=False,
    )

    # form.fieldset('default',
    #              label=u'Item Description',
    #         fields=['acronym', 'title', 'description', 'long_description',
    #                 'keywords', 'sectors', 'climate_impacts', 'elements',
    #                 ]
    #         )

    logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(
            u"Upload a representative picture or logo for the item."
            u" Recommended size: at least 360/180 px, aspect ratio 2x"
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
        default={
            "items": organisation_layout_items
        },
        required=False,
    )

alsoProvides(IOrganisation["acronym"], ILanguageIndependentField)
alsoProvides(IOrganisation["contact"], ILanguageIndependentField)
alsoProvides(IOrganisation["organisational_websites"], ILanguageIndependentField)
alsoProvides(IOrganisation["organisational_contact_information"], ILanguageIndependentField)
alsoProvides(IOrganisation["logo"], ILanguageIndependentField)
