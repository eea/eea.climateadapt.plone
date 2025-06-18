from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm  # , IFieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import Interface, alsoProvides  # , implementer  # , implements
from zope.schema import Bool, Choice, Date, List, Text, TextLine, Tuple

from eea.climateadapt import CcaAdminMessageFactory as _

ADD_ORGANISATION_URL = (
    "<a target='_blank' "
    "href='/metadata/organisations/++add++eea.climateadapt.organisation'>"
    "click here</a>"
)


class IAceMeasure(Interface, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Measure
    """

    # -----------[ "default" fields ]------------------

    title = TextLine(
        title=_("Title"),
        description=_(
            "Name of the case study clearly "
            "identifying its scope and location "
            "(250 character limit)"
        ),
        required=True,
    )

    long_description = RichText(
        title=_("Description"),
        required=True,
    )

    description = Text(
        title=_("Short summary"),
        required=False,
        description="Enter a short summary that will be used in listings.",
        missing_value="",
    )

    directives.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_("Climate impacts"),
        missing_value=[],
        default=None,
        description=_(
            "Select one or more climate change impact topics that this item relates to:"
        ),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    keywords = Tuple(
        title=_("Keywords"),
        description=_(
            "Describe and tag this item with relevant keywords. "
            "Press Enter after writing your keyword. "
            "Use specific and not general key words (e.g. avoid "
            "words as: adaption, climate change, measure, "
            "integrated approach, etc.):"
        ),
        required=False,
        default=(),
        value_type=TextLine(
            title="Single topic",
        ),
        missing_value=(None),
    )

    directives.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Sectors"),
        description=_(
            "Select one or more relevant sector policies that this item relates to:"
        ),
        required=True,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
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

    # -----------[ "additional_details" fields ]------------------

    # dexteritytextindexer.searchable("stakeholder_participation")
    stakeholder_participation = RichText(
        title=_("Stakeholder participation"),
        required=False,
        default="",
        description=_(
            "Describe the Information about actors involved, the "
            "form of participation and the participation process. "
            " Focus should be on the level of participation needed "
            "and/or adopted already (from information, to full "
            "commitment in the deliberation/implementation "
            "process), with useful notes e.g. regarding "
            "motivations. (5,000 character limit)"
        ),
    )

    # dexteritytextindexer.searchable("success_limitations")
    success_limitations = RichText(
        title=_("Success and limiting factors"),
        required=False,
        default="",
        description=_(
            "Describe factors that are decisive for a successful "
            "implementation and expected challenges or limiting "
            "factors which may hinder the process and need to be "
            "considered (5,000 character limit)"
        ),
    )

    # dexteritytextindexer.searchable("cost_benefit")
    cost_benefit = RichText(
        title=_("Costs and benefits"),
        required=False,
        default="",
        description=_(
            "Describe costs (possibly providing quantitative "
            "estimate) and funding sources. Describe benefits "
            "provided by implemented solutions, i.e.: positive "
            "outcomes related climate change adaptation, "
            "co-benefits in other areas, quantitative estimation "
            "of benefits and related methodologies (e.g. "
            "monetization of benefits for cost benefit analysis, "
            "indicators of effectiveness of actions implemented, "
            "etc.) (5,000 characters limit)"
        ),
    )

    # dexteritytextindexer.searchable("legal_aspects")
    legal_aspects = RichText(
        title=_("Legal aspects"),
        required=False,
        default="",
        description=_(
            "Describe the Legislation "
            "framework from which the case "
            "originated, relevant institutional"
            " opportunities and constrains, "
            "which determined the case as it "
            "is (5000 character limit):"
        ),
    )

    # dexteritytextindexer.searchable("implementation_time")
    implementation_time = RichText(
        title=_("Implementation time"),
        required=False,
        default=None,
        description=_(
            "Describe the time needed to implement the measure. "
            "Include: Time frame, e.g. 5-10 years, Brief "
            "explanation(250 char limit)"
        ),
    )

    # dexteritytextindexer.searchable("lifetime")
    lifetime = RichText(
        title=_("Lifetime"),
        required=False,
        default="",
        description="Describe the lifetime of the measure: "
        "Time frame, e.g. 5-10 years, Brief explanation "
        "(250 char limit)",
    )

    # -----------[ "reference_information" fields ]------------------

    directives.widget("websites", TextLinesWidget)
    websites = Tuple(
        title=_("Websites"),
        description=_(
            "List the Websites where the option can be found"
            " or is described. Note: may refer to the original "
            "document describing a measure and does not have to "
            "refer back to the project e.g. collected measures. "
            "NOTE: Add http:// in front of every website link."
        ),
        required=False,
        # TODO: plone6 needs to be a URI
        value_type=TextLine(),
        # missing_value=(),
    )

    # dexteritytextindexer.searchable("source")
    source = TextLine(
        title=_("References"),
        required=False,
        description=_(
            "Describe the references (projects, a tools reports, etc.) "
            "related to this item, providing further information about "
            "it or its source."
        ),
    )

    # -----------[ "geographic_information" fields ]------------------

    directives.widget(governance_level="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    governance_level = List(
        title=_("Governance Level"),
        description=_(
            "Select the one governance level that relates to this adaptation option"
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_governancelevel",
        ),
    )

    # directives.widget(geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
    geochars = Text(
        title=_("Geographic characterisation"),
        required=True,
        default="""{
                    "geoElements":{"element":"GLOBAL",
                    "macrotrans":null,"biotrans":null,"countries":[],
                    "subnational":[],"city":""}}""",
        description="Select the characterisation for this item",
    )

    comments = Text(
        title=_("Comments"),
        required=False,
        default="",
        description=_(
            "Comments about this database item "
            "[information entered below will not be "
            "displayed on the public pages of "
            "climate-adapt]"
        ),
    )

    origin_website = List(
        title=_("Item from third parties"),
        description=_(
            "Used only to highlight items "
            "provided by Third parties. "
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

    # TODO: this will be a widget
    other_contributor = Text(
        title=_("Other contributor(s)"),
        required=False,
        default="",
        description=_(
            "Please first verify if the contributor is "
            "already part of the Climate ADAPT Database."
            " If not, it is suggested to first create a "
            "new Organisation item (%s). As last"
            " alternative please add the new "
            "contributor(s) in the following box, using "
            "the official name" % ADD_ORGANISATION_URL
        ),
    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IEditForm, "implementation_type")
    directives.omitted(IAddForm, "implementation_type")
    directives.omitted(IEditForm, "spatial_layer")
    directives.omitted(IAddForm, "spatial_layer")
    directives.omitted(IEditForm, "spatial_values")
    directives.omitted(IAddForm, "spatial_values")
    directives.omitted(IEditForm, "measure_type")
    directives.omitted(IAddForm, "measure_type")
    directives.omitted(IEditForm, "important")
    directives.omitted(IAddForm, "important")
    # end

    implementation_type = Choice(
        title=_("Implementation Type"),
        required=False,
        default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype",
    )

    spatial_layer = TextLine(title=_("Spatial Layer"), required=False, default="")

    spatial_values = List(
        title=_("Countries"),
        description=_("European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    # TODO: startdate, enddate, publicationdate have no values in DB
    # TODO: specialtagging is not used in any view jsp, only in add and edit
    # views

    directives.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation approaches"),
        description=_("Select one or more approaches."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    measure_type = Choice(
        title=_("Measure Type"),
        required=False,
        default="A",
        vocabulary="eea.climateadapt.acemeasure_types",
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

    important = Bool(title=_("High importance"), required=False, default=False)

    # rating = Int(title=_("Rating"), required=True, default=0)

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


alsoProvides(IAceMeasure["climate_impacts"], ILanguageIndependentField)
alsoProvides(IAceMeasure["comments"], ILanguageIndependentField)
alsoProvides(IAceMeasure["contributor_list"], ILanguageIndependentField)
alsoProvides(IAceMeasure["elements"], ILanguageIndependentField)
alsoProvides(IAceMeasure["geochars"], ILanguageIndependentField)
alsoProvides(IAceMeasure["governance_level"], ILanguageIndependentField)
alsoProvides(IAceMeasure["health_impacts"], ILanguageIndependentField)
alsoProvides(IAceMeasure["include_in_mission"], ILanguageIndependentField)
alsoProvides(IAceMeasure["include_in_observatory"], ILanguageIndependentField)
alsoProvides(IAceMeasure["keywords"], ILanguageIndependentField)
alsoProvides(IAceMeasure["origin_website"], ILanguageIndependentField)
alsoProvides(IAceMeasure["other_contributor"], ILanguageIndependentField)
alsoProvides(IAceMeasure["publication_date"], ILanguageIndependentField)
alsoProvides(IAceMeasure["sectors"], ILanguageIndependentField)
alsoProvides(IAceMeasure["special_tags"], ILanguageIndependentField)
alsoProvides(IAceMeasure["websites"], ILanguageIndependentField)
alsoProvides(IAceMeasure["implementation_type"], ILanguageIndependentField)
alsoProvides(IAceMeasure["important"], ILanguageIndependentField)
alsoProvides(IAceMeasure["measure_type"], ILanguageIndependentField)
alsoProvides(IAceMeasure["spatial_layer"], ILanguageIndependentField)
alsoProvides(IAceMeasure["spatial_values"], ILanguageIndependentField)

# blobs are handled by field serializer
# alsoProvides(IAceMeasure["image"], ILanguageIndependentField)
# alsoProvides(IAceMeasure["logo"], ILanguageIndependentField)

# alsoProvides(IAceMeasure["rating"], ILanguageIndependentField)
# alsoProvides(IAceMeasure["featured"], ILanguageIndependentField)
