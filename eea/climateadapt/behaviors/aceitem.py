from plone.app.dexterity.behaviors.metadata import IPublication
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm  # , IFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import alsoProvides  # , implementer
from zope.schema import (
    Bool,
    Choice,
    Date,
    List,
    Text,
    TextLine,
    Tuple,
)

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.schema import AbsoluteUrl, Uploader


class IAceItem(IImageScaleTraversable):
    """
    Defines content-type schema for Ace Item
    """

    directives.omitted(IAddForm, "relatedItems")
    directives.omitted(IEditForm, "relatedItems")

    # -----------[ "default" fields ]------------------
    # these are the richtext fields from the db:
    set(
        [
            "description",
            "storedat",
            "admincomment",
            "comments",
            "source",
            "keyword",
            "textsearch",
        ]
    )

    origin_website = List(
        title=_("Item from third parties"),
        description=_(
            "Used only to highlight items "
            "provided by Third parties."
            "<br>Please don't compile "
            "this field if you are a Climate-ADAPT expert "
            "creating a new item."
        ),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.origin_website"),
    )

    logo = NamedBlobImage(
        title=_("Logo"),
        description=_(
            "Upload a representative picture or logo for the item."
            " Recommended size: at least 360/180 px, aspect ratio 2x"
        ),
        required=False,
    )

    image = NamedBlobImage(
        title=_("Thumbnail"),
        description=_(
            "Upload a representative picture or logo for the item. "
            "Recommended size: at least 360/180 px, aspect ratio 2x. "
            "This image will be used in the search result page - cards view. "
            "If this image doesn't exist, then the logo image will be used."
        ),
        required=False,
    )

    health_impacts = List(
        title=_("Health impacts"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.health_impacts"),
    )
    include_in_observatory = Bool(
        title=_("Include in observatory"), required=False, default=False
    )

    include_in_mission = Bool(
        title=_("Include in the Mission Portal"), required=False, default=False
    )

    title = TextLine(
        title=_("Title"),
        description=_("Item Name (250 character limit)"),
        required=True,
    )

    long_description = RichText(
        title=_("Description"),
        description=_("Provide a description of the item.(5,000 character limit)"),
        required=True,
    )

    description = Text(
        title=_("Short summary"),
        required=False,
        description=_("Enter a short summary that will be used in listings."),
        missing_value=str(""),
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    keywords = Tuple(
        title=_("Keywords"),
        description=_(
            "Describe and tag this item with relevant keywords."
            "Press Enter after writing your keyword."
        ),
        required=False,
        missing_value=None,
        default=(),
        value_type=TextLine(
            title=_("Single topic"),
        ),
    )

    directives.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Sectors"),
        description=_(
            "Select one or more relevant sector policies that this item relates to."
        ),
        required=True,  # TODO: set to False for the migration to plone6
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    directives.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_("Climate impacts"),
        description=_(
            "Select one or more climate change impact topics that this item relates to."
        ),
        required=True,  # TODO: set to False for the migration to plone6
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    directives.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation approaches"),
        description=_("Select one or more approaches."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    publication_date = Date(
        title=_("Date of item's creation"),
        description=_(
            "The date refers to the moment in which the item "
            "has been prepared by contributing experts to be "
            "submitted for the publication in Climate "
            "ADAPT Publication/last update date."
            " Please use the Calendar icon to add day/month/year. If you want to "
            'add only the year, please select "day: 1", "month: January" '
            "and then the year"
        ),
        required=True,  # TODO: set to False for the migration to plone6
    )

    # -----------[ "reference_information" fields ]------------------

    directives.widget("websites", TextLinesWidget)
    websites = Tuple(
        title=_("Websites"),
        description=_(
            "List the Websites where the item can be found or is "
            "described. Please place each website on a new line"
        ),
        required=False,
        # URI # TODO: plone6 needs to be fixed, some URLs are not valid URI
        value_type=TextLine(),
        # missing_value=None,
    )

    source = RichText(
        title=_("References"),
        required=False,
        description=_(
            "Describe the references (projects, a tools reports, etc.) "
            "related to this item, providing further information about "
            "it or its source."
        ),
    )

    # -----------[ "geographic_information" fields ]------------------

    # directives.widget(
    #     geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
    geochars = Text(
        title=_("Geographic characterisation"),
        required=True,
        default=str(
            '{"geoElements":{"element":"GLOBAL", "macrotrans"'
            ':null,"biotrans":null,"countries":[],'
            '"subnational":[],"city":""}}'
        ),
        description=_("Select the characterisation for this item"),
    )

    comments = Text(
        title=_("Comments"),
        required=False,
        default=str(""),
        description=_(
            "Comments about this database item "
            "[information entered below will not be "
            "displayed on the public pages of "
            "climate-adapt]"
        ),
    )

    contributor_list = RelationList(
        title=_("Contributor(s)"),
        default=[],
        description=_(
            'Select from the Climate ADAPT "Organisation" items'
            " the organisations contributing to/ involved in this"
            " item"
        ),
        value_type=RelationChoice(
            title=_("Related"),
            vocabulary="eea.climateadapt.organisations",
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    other_contributor = Text(
        title=_("Other contributor(s)"),
        required=False,
        default=str(""),
        description=_(
            "Please first verify if the contributor is "
            "already part of the Climate ADAPT Database."
            " If not, it is suggested to first create a "
            "new Organisation item "
            "(<a target='_blank' "
            "href='/metadata/organisations/++add++eea.climateadapt.organisation'>click here</a>). "
            "As last alternative please add the new "
            "contributor(s) in the following box, using "
            "the official name"
        ),
    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IAddForm, "item_link")
    directives.omitted(IEditForm, "item_link")

    directives.omitted(IAddForm, "uploader")
    directives.omitted(IEditForm, "uploader")

    directives.omitted(IAddForm, "data_type")
    directives.omitted(IEditForm, "data_type")

    directives.omitted(IAddForm, "storage_type")
    directives.omitted(IEditForm, "storage_type")

    directives.omitted(IAddForm, "spatial_layer")
    directives.omitted(IEditForm, "spatial_layer")

    directives.omitted(IAddForm, "spatial_values")
    directives.omitted(IEditForm, "spatial_values")

    # directives.omitted(IAddForm, "important")
    # directives.omitted(IEditForm, "important")

    directives.omitted(IAddForm, "metadata")
    directives.omitted(IEditForm, "metadata")

    # -----------[ "backend" fields ]------------------

    special_tags = Tuple(
        title=_("Special tagging"),
        description=_(
            "Used only by Climate-ADAPT administrator. Please don't "
            "compile this field if you are a Climate-ADAPT expert creating a new "
            "item."
        ),
        required=False,
        value_type=TextLine(),
        missing_value=None,
    )

    item_link = AbsoluteUrl(title=_("Item link"), required=False, default=str(""))

    uploader = Uploader(title=_("Uploaded by"), required=False, default=str(""))
    # fix???
    data_type = Choice(
        title=_("Data Type"),
        required=False,
        vocabulary="eea.climateadapt.aceitems_datatypes",
    )

    # fix???
    storage_type = Choice(
        title=_("Storage Type"),
        required=False,
        vocabulary="eea.climateadapt.aceitems_storagetypes",
    )

    spatial_layer = TextLine(title=_("Spatial Layer"), required=False, default=str(""))

    spatial_values = List(
        title=_("Countries"),
        description=_("European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    metadata = TextLine(
        title=_("Metadata"),
        required=False,
    )


alsoProvides(IAceItem["climate_impacts"], ILanguageIndependentField)
alsoProvides(IAceItem["comments"], ILanguageIndependentField)
alsoProvides(IAceItem["contributor_list"], ILanguageIndependentField)
alsoProvides(IAceItem["data_type"], ILanguageIndependentField)
alsoProvides(IAceItem["elements"], ILanguageIndependentField)
alsoProvides(IAceItem["geochars"], ILanguageIndependentField)
alsoProvides(IAceItem["health_impacts"], ILanguageIndependentField)
# alsoProvides(IAceItem["important"], ILanguageIndependentField)
alsoProvides(IAceItem["include_in_mission"], ILanguageIndependentField)
alsoProvides(IAceItem["include_in_observatory"], ILanguageIndependentField)
alsoProvides(IAceItem["item_link"], ILanguageIndependentField)
alsoProvides(IAceItem["keywords"], ILanguageIndependentField)
alsoProvides(IAceItem["metadata"], ILanguageIndependentField)
alsoProvides(IAceItem["origin_website"], ILanguageIndependentField)
alsoProvides(IAceItem["other_contributor"], ILanguageIndependentField)
alsoProvides(IAceItem["publication_date"], ILanguageIndependentField)
alsoProvides(IAceItem["sectors"], ILanguageIndependentField)
alsoProvides(IAceItem["spatial_values"], ILanguageIndependentField)
alsoProvides(IAceItem["special_tags"], ILanguageIndependentField)
alsoProvides(IAceItem["storage_type"], ILanguageIndependentField)
alsoProvides(IAceItem["uploader"], ILanguageIndependentField)
alsoProvides(IAceItem["websites"], ILanguageIndependentField)
alsoProvides(IAceItem["spatial_layer"], ILanguageIndependentField)

alsoProvides(IPublication["effective"], ILanguageIndependentField)
alsoProvides(IPublication["expires"], ILanguageIndependentField)

# alsoProvides(IAceItem["featured"], ILanguageIndependentField)
# blobs are no longer ilanguage independent because we treat them in serializer
# alsoProvides(IAceItem["image"], ILanguageIndependentField)
# alsoProvides(IAceItem["logo"], ILanguageIndependentField)
