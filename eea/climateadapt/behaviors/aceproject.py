import json

from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm  # , IFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import Interface, alsoProvides  # , implementer
from zope.schema import (
    URI,
    Bool,
    Choice,
    Date,
    List,
    Text,
    TextLine,
    Tuple,
)

from eea.climateadapt import CcaAdminMessageFactory as _

from .volto_layout import aceproject_layout_blocks, aceproject_layout_items

GEOCHARS = {
    "geoElements": {
        "element": "GLOBAL",
        "macrotrans": None,
        "biotrans": None,
        "countries": [],
        "subnational": [],
        "city": "",
    }
}


class IAceProject(Interface, IImageScaleTraversable, IBlocks):
    """
    Defines content-type schema for Ace Project
    """

    # -----------[ "default" fields ]------------------

    # These fields are richtext in the db:
    # set(['keywords', 'partners', 'admincomment', 'abstracts', 'source'])
    origin_website = List(
        title=_("Item from third parties"),
        description=_(
            "Used only to highlight items "
            "provided by Third parties. "
            "Please don't compile "
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

    contributor_list = RelationList(
        title="Contributor(s)",
        default=[],
        description=_(
            "Select from the Climate ADAPT Organisation items the "
            "organisations contributing to/ involved in this item"
        ),
        value_type=RelationChoice(
            title=_("Related"),
            vocabulary="eea.climateadapt.organisations",
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    funding_programme = Choice(
        title=_("Funding Programme"),
        required=False,
        # value_type = Choice(
        vocabulary="eea.climateadapt.funding_programme",
        #    )
    )

    acronym = TextLine(
        title=_("Acronym"),
        description=_("Acronym of the project"),
        required=True,
    )

    title = TextLine(
        title=_("Title"),
        description=_("Project title or name"),
        required=True,
    )

    # dexteritytextindexer.searchable("long_description")
    long_description = RichText(
        title=_("Abstracts"),
        description=_(
            "Provide information focusing on project output. "
            "Possibly on specific Website features."
        ),
        required=True,
    )

    lead = TextLine(
        title=_("Lead"),
        description=_("Lead organisation or individual of the project"),
        required=True,
    )

    # dexteritytextindexer.searchable("partners")
    partners = RichText(
        title=_("Partners"),
        description=_(
            "Provide information about project partners (organisation names)."
        ),
        required=True,
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    # dexteritytextindexer.searchable("keywords")
    keywords = Tuple(
        title=_("Keywords"),
        description=_(
            "Provide Keywords related to the project. "
            "Press Enter after writing your keyword."
        ),
        required=False,
        default=(),
        value_type=TextLine(
            title="Single topic",
        ),
        missing_value=(None),
    )

    health_impacts = List(
        title=_("Health impacts"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.health_impacts"),
    )

    publication_date = Date(
        title=_("Date of item's creation"),
        description="The date refers to the moment in which the item "
        "has been prepared by contributing expeerts to be "
        "submitted for the publication in Climate "
        "ADAPTPublication/last update date."
        " Please use the Calendar icon to add day/month/year. If you want to "
        'add only the year, please select "day: 1", "month: January" '
        "and then the year",
        required=True,
    )

    include_in_observatory = Bool(
        title=_("Include in observatory"), required=False, default=False
    )

    include_in_mission = Bool(
        title=_("Include in the Mission Portal"), required=False, default=False
    )

    directives.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Sectors"),
        description=_(
            "Select one or more relevant sector policies that this item relates to."
        ),
        required=True,
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
        missing_value=[],
        default=None,
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    directives.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation elements"),
        description=_("Select one or more elements."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    funding = TextLine(
        title=_("Further information on the funding"),
        description=_("Provide source of funding"),
        required=False,
    )

    duration = TextLine(
        title=_("Duration"),
        description=_("Provide duration of project - Start and end date [yr]"),
        required=False,
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
        value_type=TextLine(title="Website"),  # URI(), #plone6 compatibility
        # missing_value=(),
    )

    # dexteritytextindexer.searchable("source")
    source = TextLine(
        title=_("Reference"),
        description=_(
            "Provide source from which project was retrieved (e.g. specific DB) "
        ),
        required=False,
    )

    # -----------[ "geographic_information" fields ]------------------
    # directives.widget(
    #     geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
    geochars = Text(
        title=_("Geographic characterisation"),
        required=True,
        default=str(json.dumps(GEOCHARS)),
        description="Select the characterisation for this item",
    )

    comments = Text(
        title=_("Source"),
        description=_(
            "Comments about this database item [information entered"
            " below will not be displayed on the public pages of "
            "climate-adapt]"
        ),
        required=False,
    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IEditForm, "specialtagging")
    directives.omitted(IAddForm, "specialtagging")
    directives.omitted(IEditForm, "important")
    directives.omitted(IAddForm, "important")
    directives.omitted(IEditForm, "spatial_layer")
    directives.omitted(IAddForm, "spatial_layer")
    directives.omitted(IEditForm, "spatial_values")
    directives.omitted(IAddForm, "spatial_values")
    directives.omitted(IAddForm, "id")
    directives.omitted(IEditForm, "id")

    # end

    id = TextLine(
        title=_("Object ID"),
        required=False,
    )

    specialtagging = TextLine(
        title=_("Special Tagging"),
        description=_(
            "Used only by Climate-ADAPT administrator. Please don't compile this field if you are a Climate-ADAPT expert creating a new item"
        ),
        required=False,
    )

    special_tags = Tuple(
        title=_("Special tagging"),
        description=_(
            "Used only by Climate-ADAPT administrator. Please don't "
            "compile this field if you are a Climate-ADAPT expert creating a new "
            "item."
        ),
        required=False,
        value_type=TextLine(),
        missing_value=(None),
    )

    important = Bool(
        title=_("Important"),
        required=False,
        default=False,
    )

    # rating = Int(title=_(u"Rating"), required=True, default=0)

    spatial_layer = TextLine(
        title=_("Spatial Layer"),
        required=False,
        default="",
    )

    spatial_values = List(
        title=_("Countries"),
        description=_("European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    partners_source_link = URI(
        title=_("Partners Source Link"),
        description=("Provide URL from project partners"),
        required=False,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=aceproject_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={"items": aceproject_layout_items},
        required=False,
    )


alsoProvides(IAceProject["acronym"], ILanguageIndependentField)
alsoProvides(IAceProject["climate_impacts"], ILanguageIndependentField)
alsoProvides(IAceProject["comments"], ILanguageIndependentField)
alsoProvides(IAceProject["contributor_list"], ILanguageIndependentField)
alsoProvides(IAceProject["duration"], ILanguageIndependentField)
alsoProvides(IAceProject["elements"], ILanguageIndependentField)
alsoProvides(IAceProject["funding"], ILanguageIndependentField)
alsoProvides(IAceProject["funding_programme"], ILanguageIndependentField)
alsoProvides(IAceProject["geochars"], ILanguageIndependentField)
alsoProvides(IAceProject["health_impacts"], ILanguageIndependentField)
alsoProvides(IAceProject["id"], ILanguageIndependentField)
alsoProvides(IAceProject["important"], ILanguageIndependentField)
alsoProvides(IAceProject["include_in_mission"], ILanguageIndependentField)
alsoProvides(IAceProject["include_in_observatory"], ILanguageIndependentField)
alsoProvides(IAceProject["keywords"], ILanguageIndependentField)
alsoProvides(IAceProject["lead"], ILanguageIndependentField)
alsoProvides(IAceProject["origin_website"], ILanguageIndependentField)
alsoProvides(IAceProject["partners"], ILanguageIndependentField)
alsoProvides(IAceProject["partners_source_link"], ILanguageIndependentField)
alsoProvides(IAceProject["publication_date"], ILanguageIndependentField)
alsoProvides(IAceProject["sectors"], ILanguageIndependentField)
alsoProvides(IAceProject["spatial_layer"], ILanguageIndependentField)
alsoProvides(IAceProject["spatial_values"], ILanguageIndependentField)
alsoProvides(IAceProject["special_tags"], ILanguageIndependentField)
alsoProvides(IAceProject["specialtagging"], ILanguageIndependentField)
alsoProvides(IAceProject["websites"], ILanguageIndependentField)

# blobs are handled by field serializer
# alsoProvides(IAceProject["image"], ILanguageIndependentField)
# alsoProvides(IAceProject["logo"], ILanguageIndependentField)
#
# alsoProvides(IAceProject["modification_date"], ILanguageIndependentField)
# alsoProvides(IAceProject["rating"], ILanguageIndependentField)
# alsoProvides(IAceProject["creation_date"], ILanguageIndependentField)
# alsoProvides(IAceProject["featured"], ILanguageIndependentField)
