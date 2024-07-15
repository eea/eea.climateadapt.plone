from collective import dexteritytextindexer
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield import RichText
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.autoform import directives
from plone.directives import form
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm, IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.component import adapter
from zope.interface import alsoProvides, implementer  # , implements
from zope.schema import URI, Bool, Choice, Date, List, Text, TextLine, Tuple  # Int,

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.widgets.ajaxselect import BetterAjaxSelectWidget

# from plone.autoform import directives

ADD_ORGANISATION_URL = (
    "<a target='_blank' "
    "href='/metadata/organisations/++add++eea.climateadapt.organisation'>"
    "click here</a>"
)


class IAceMeasure(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Measure
    """

    dexteritytextindexer.searchable("challenges")
    dexteritytextindexer.searchable("climate_impacts")
    dexteritytextindexer.searchable("contact")
    dexteritytextindexer.searchable("cost_benefit")
    dexteritytextindexer.searchable("geochars")
    dexteritytextindexer.searchable("implementation_time")
    dexteritytextindexer.searchable("important")
    dexteritytextindexer.searchable("keywords")
    dexteritytextindexer.searchable("legal_aspects")
    dexteritytextindexer.searchable("lifetime")
    dexteritytextindexer.searchable("long_description")
    dexteritytextindexer.searchable("description")
    dexteritytextindexer.searchable("measure_type")
    dexteritytextindexer.searchable("objectives")
    dexteritytextindexer.searchable("sectors")
    dexteritytextindexer.searchable("solutions")
    dexteritytextindexer.searchable("source")
    dexteritytextindexer.searchable("spatial_layer")
    dexteritytextindexer.searchable("spatial_values")
    dexteritytextindexer.searchable("special_tags")
    dexteritytextindexer.searchable("stakeholder_participation")
    dexteritytextindexer.searchable("success_limitations")
    dexteritytextindexer.searchable("title")
    dexteritytextindexer.searchable("websites")
    # dexteritytextindexer.searchable('year')
    dexteritytextindexer.searchable("publication_date")

    form.fieldset(
        "default",
        label="Item Description",
        fields=[
            "publication_date",
            "title",
            "long_description",
            "description",
            "climate_impacts",
            "keywords",
            "sectors",
            "elements",
            "featured",  # 'year',
        ],
    )

    form.fieldset(
        "additional_details",
        label="Additional Details",
        fields=[
            "stakeholder_participation",
            "success_limitations",
            "cost_benefit",
            "legal_aspects",
            "implementation_time",
            "lifetime",
        ],
    )

    # form.fieldset('inclusion_health_observatory',
    #              label=u'Inclusion in health observatory',
    #              fields=['include_in_observatory', 'health_impacts']
    #              )

    form.fieldset(
        "reference_information",
        label="Reference information",
        fields=["websites", "source", "special_tags",
                "comments"],  # 'contact',
    )

    # richtext fields in database:
    # set(['legalaspects', 'implementationtime', 'description', 'source',
    # 'objectives', 'stakeholderparticipation', 'admincomment', 'comments',
    # 'challenges', 'keywords', 'contact', 'solutions', 'costbenefit',
    # 'succeslimitations', 'lifetime'])

    form.fieldset(
        "geographic_information",
        label="Geographic Information",
        fields=["governance_level", "geochars"],
    )

    form.fieldset(
        "categorization",
        label="Inclusion in the Health Observatory",
        fields=["include_in_observatory",
                "include_in_mission", "health_impacts"],
    )

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

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_("Climate impacts"),
        missing_value=[],
        default=None,
        description=_(
            "Select one or more climate change impact topics that "
            "this item relates to:"
        ),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    keywords = Tuple(
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

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_("Sectors"),
        description=_(
            "Select one or more relevant sector policies" " that this item relates to:"
        ),
        required=True,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    # year = Year(title=_(u"Year"),
    # description=u"Date of publication/release/update of the items "
    # u"related source",
    # required=False,)

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

    featured = Bool(
        title=_("Featured"),
        description="Feature in search and Case Study Search Tool",
        required=False,
        default=False,
    )

    # -----------[ "additional_details" fields ]------------------

    dexteritytextindexer.searchable("stakeholder_participation")
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

    dexteritytextindexer.searchable("success_limitations")
    success_limitations = RichText(
        title=_("Success / limitations"),
        required=False,
        default="",
        description=_(
            "Describe factors that are decisive for a successful "
            "implementation and expected challenges or limiting "
            "factors which may hinder the process and need to be "
            "considered (5,000 character limit)"
        ),
    )

    dexteritytextindexer.searchable("cost_benefit")
    cost_benefit = RichText(
        title=_("Cost / Benefit"),
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

    dexteritytextindexer.searchable("legal_aspects")
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

    dexteritytextindexer.searchable("implementation_time")
    implementation_time = RichText(
        title=_("Implementation Time"),
        required=False,
        default=None,
        description=_(
            "Describe the time needed to implement the measure. "
            "Include: Time frame, e.g. 5-10 years, Brief "
            "explanation(250 char limit)"
        ),
    )

    dexteritytextindexer.searchable("lifetime")
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
        value_type=URI(),
        # missing_value=(),
    )

    dexteritytextindexer.searchable("source")
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

    form.widget(governance_level="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    governance_level = List(
        title=_("Governance Level"),
        description=_(
            "Select the one governance level that relates to this " "adaptation option"
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_governancelevel",
        ),
    )

    form.widget(geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
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

    # for name in [
    #         'implementation_type',
    #         'spatial_layer',
    #         'spatial_values',
    #         'elements',
    #         'measure_type',
    #         'important',
    #         'rating',
    #         'modification_date',
    #         'creation_date',
    #         'id'
    # ]:
    #     directives.omitted(IEditForm, name)
    #     directives.omitted(IAddForm, name)

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
    # directives.omitted(IEditForm, "rating")
    # directives.omitted(IAddForm, "rating")
    # directives.omitted(IAddForm, "modification_date")
    # directives.omitted(IEditForm, "modification_date")
    # directives.omitted(IAddForm, "creation_date")
    # directives.omitted(IEditForm, "creation_date")
    # directives.omitted(IAddForm, "id")
    # directives.omitted(IEditForm, "id")
    # end

    implementation_type = Choice(
        title=_("Implementation Type"),
        required=False,
        default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype",
    )

    spatial_layer = TextLine(title=_("Spatial Layer"),
                             required=False, default="")

    spatial_values = List(
        title=_("Countries"),
        description=_("European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    # TODO: startdate, enddate, publicationdate have no values in DB
    # TODO: specialtagging is not used in any view jsp, only in add and edit
    # views

    form.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_("Adaptation elements"),
        description=_("Select one or more elements."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    measure_type = Choice(
        title=_("Measure Type"),
        required=True,
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

    # creation_date = Datetime(
    #     title=_(u"Created"),
    #     required=False,
    # )
    #
    # modification_date = Datetime(
    #     title=_(u"Last Modified"),
    #     required=False,
    # )
    #
    # id = TextLine(
    #     title=_(u"Object ID"),
    #     required=False,
    # )

    publication_date = Date(
        title=_("Date of item's creation"),
        description="The date refers to the moment in which the item "
        "has been prepared or  updated by contributing "
        "experts to be submitted for the publication in "
        "Climate ADAPT."
        " Please use the Calendar icon to add day/month/year. If you want to "
        'add only the year, please select "day: 1", "month: January" '
        "and then the year",
        required=True,
    )

    # dexteritytextindexer.searchable('summary')
    # summary = Text(title=_(u"Summary"), required=False, default=u"")


@adapter(getSpecification(IAceMeasure["keywords"]), IWidgetsLayer)
@implementer(IFieldWidget)
def KeywordsFieldWidget(field, request):
    """The vocabulary view is overridden so that
    the widget will work properly
    Check browser/overrides.py for more details
    """
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = "eea.climateadapt.keywords"

    return widget


@adapter(getSpecification(IAceMeasure["special_tags"]), IWidgetsLayer)
@implementer(IFieldWidget)
def SpecialTagsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = "eea.climateadapt.special_tags"

    return widget


alsoProvides(IAceMeasure["climate_impacts"], ILanguageIndependentField)
alsoProvides(IAceMeasure["comments"], ILanguageIndependentField)
alsoProvides(IAceMeasure["contributor_list"], ILanguageIndependentField)
alsoProvides(IAceMeasure["elements"], ILanguageIndependentField)
alsoProvides(IAceMeasure["featured"], ILanguageIndependentField)
alsoProvides(IAceMeasure["geochars"], ILanguageIndependentField)
alsoProvides(IAceMeasure["governance_level"], ILanguageIndependentField)
alsoProvides(IAceMeasure["health_impacts"], ILanguageIndependentField)
alsoProvides(IAceMeasure["image"], ILanguageIndependentField)
alsoProvides(IAceMeasure["include_in_mission"], ILanguageIndependentField)
alsoProvides(IAceMeasure["include_in_observatory"], ILanguageIndependentField)
alsoProvides(IAceMeasure["keywords"], ILanguageIndependentField)
alsoProvides(IAceMeasure["logo"], ILanguageIndependentField)
alsoProvides(IAceMeasure["origin_website"], ILanguageIndependentField)
alsoProvides(IAceMeasure["other_contributor"], ILanguageIndependentField)
alsoProvides(IAceMeasure["publication_date"], ILanguageIndependentField)
alsoProvides(IAceMeasure["sectors"], ILanguageIndependentField)
alsoProvides(IAceMeasure["special_tags"], ILanguageIndependentField)
alsoProvides(IAceMeasure["websites"], ILanguageIndependentField)
alsoProvides(IAceMeasure["implementation_type"], ILanguageIndependentField)
alsoProvides(IAceMeasure["important"], ILanguageIndependentField)
alsoProvides(IAceMeasure["measure_type"], ILanguageIndependentField)
# alsoProvides(IAceMeasure["rating"], ILanguageIndependentField)
alsoProvides(IAceMeasure["spatial_layer"], ILanguageIndependentField)
alsoProvides(IAceMeasure["spatial_values"], ILanguageIndependentField)


alsoProvides(IGeolocatable["geolocation"], ILanguageIndependentField)
