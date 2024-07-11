from collective import dexteritytextindexer
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.widgets.ajaxselect import BetterAjaxSelectWidget
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
from zope.schema import (URI, Bool, Choice, Date, Int, List, Text, TextLine,
                         Tuple)
from plone.autoform import directives

ADD_ORGANISATION_URL = (
    u"<a target='_blank' "
    u"href='/metadata/organisations/++add++eea.climateadapt.organisation'>"
    u"click here</a>"
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
        label=u"Item Description",
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
        label=u"Additional Details",
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
        label=u"Reference information",
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
        label=u"Geographic Information",
        fields=["governance_level", "geochars"],
    )

    form.fieldset(
        "categorization",
        label=u"Inclusion in the Health Observatory",
        fields=["include_in_observatory",
                "include_in_mission", "health_impacts"],
    )

    # -----------[ "default" fields ]------------------

    title = TextLine(
        title=_(u"Title"),
        description=_(
            u"Name of the case study clearly "
            u"identifying its scope and location "
            u"(250 character limit)"
        ),
        required=True,
    )

    long_description = RichText(
        title=_(u"Description"),
        required=True,
    )

    description = Text(
        title=_(u"Short summary"),
        required=False,
        description=u"Enter a short summary that will be used in listings.",
        missing_value=u"",
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate impacts"),
        missing_value=[],
        default=None,
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to:"
        ),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    directives.widget("keywords", vocabulary="eea.climateadapt.keywords")
    keywords = Tuple(
        description=_(
            u"Describe and tag this item with relevant keywords. "
            u"Press Enter after writing your keyword. "
            u"Use specific and not general key words (e.g. avoid "
            u"words as: adaption, climate change, measure, "
            u"integrated approach, etc.):"
        ),
        required=False,
        default=(),
        value_type=TextLine(
            title=u"Single topic",
        ),
        missing_value=(None),
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_(u"Sectors"),
        description=_(
            u"Select one or more relevant sector policies"
            u" that this item relates to:"
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
        title=_(u"Date of item's creation"),
        description=u"The date refers to the moment in which the item "
        u"has been prepared by contributing expeerts to be "
        u"submitted for the publication in Climate "
        u"ADAPTPublication/last update date."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u'add only the year, please select "day: 1", "month: January" '
        u"and then the year",
        required=True,
    )

    featured = Bool(
        title=_(u"Featured"),
        description=u"Feature in search and Case Study Search Tool",
        required=False,
        default=False,
    )

    # -----------[ "additional_details" fields ]------------------

    dexteritytextindexer.searchable("stakeholder_participation")
    stakeholder_participation = RichText(
        title=_(u"Stakeholder participation"),
        required=False,
        default=u"",
        description=_(
            u"Describe the Information about actors involved, the "
            u"form of participation and the participation process. "
            u" Focus should be on the level of participation needed "
            u"and/or adopted already (from information, to full "
            u"commitment in the deliberation/implementation "
            u"process), with useful notes e.g. regarding "
            u"motivations. (5,000 character limit)"
        ),
    )

    dexteritytextindexer.searchable("success_limitations")
    success_limitations = RichText(
        title=_(u"Success / limitations"),
        required=False,
        default=u"",
        description=_(
            u"Describe factors that are decisive for a successful "
            u"implementation and expected challenges or limiting "
            u"factors which may hinder the process and need to be "
            u"considered (5,000 character limit)"
        ),
    )

    dexteritytextindexer.searchable("cost_benefit")
    cost_benefit = RichText(
        title=_(u"Cost / Benefit"),
        required=False,
        default=u"",
        description=_(
            u"Describe costs (possibly providing quantitative "
            u"estimate) and funding sources. Describe benefits "
            u"provided by implemented solutions, i.e.: positive "
            u"outcomes related climate change adaptation, "
            u"co-benefits in other areas, quantitative estimation "
            u"of benefits and related methodologies (e.g. "
            u"monetization of benefits for cost benefit analysis, "
            u"indicators of effectiveness of actions implemented, "
            u"etc.) (5,000 characters limit)"
        ),
    )

    dexteritytextindexer.searchable("legal_aspects")
    legal_aspects = RichText(
        title=_(u"Legal aspects"),
        required=False,
        default=u"",
        description=_(
            u"Describe the Legislation "
            u"framework from which the case "
            u"originated, relevant institutional"
            u" opportunities and constrains, "
            u"which determined the case as it "
            u"is (5000 character limit):"
        ),
    )

    dexteritytextindexer.searchable("implementation_time")
    implementation_time = RichText(
        title=_(u"Implementation Time"),
        required=False,
        default=None,
        description=_(
            u"Describe the time needed to implement the measure. "
            u"Include: Time frame, e.g. 5-10 years, Brief "
            u"explanation(250 char limit)"
        ),
    )

    dexteritytextindexer.searchable("lifetime")
    lifetime = RichText(
        title=_(u"Lifetime"),
        required=False,
        default=u"",
        description=u"Describe the lifetime of the measure: "
        u"Time frame, e.g. 5-10 years, Brief explanation "
        u"(250 char limit)",
    )

    # -----------[ "reference_information" fields ]------------------

    directives.widget("websites", TextLinesWidget)
    websites = Tuple(
        title=_(u"Websites"),
        description=_(
            u"List the Websites where the option can be found"
            u" or is described. Note: may refer to the original "
            u"document describing a measure and does not have to "
            u"refer back to the project e.g. collected measures. "
            u"NOTE: Add http:// in front of every website link."
        ),
        required=False,
        value_type=URI(),
        # missing_value=(),
    )

    dexteritytextindexer.searchable("source")
    source = TextLine(
        title=_(u"References"),
        required=False,
        description=_(
            u"Describe the references (projects, a tools reports, etc.) "
            u"related to this item, providing further information about "
            u"it or its source."
        ),
    )

    # -----------[ "geographic_information" fields ]------------------

    form.widget(governance_level="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    governance_level = List(
        title=_(u"Governance Level"),
        description=_(
            u"Select the one governance level that relates to this "
            u"adaptation option"
        ),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_governancelevel",
        ),
    )

    form.widget(geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
    geochars = Text(
        title=_(u"Geographic characterisation"),
        required=True,
        default=u"""{
                    "geoElements":{"element":"GLOBAL",
                    "macrotrans":null,"biotrans":null,"countries":[],
                    "subnational":[],"city":""}}""",
        description=u"Select the characterisation for this item",
    )

    comments = Text(
        title=_(u"Comments"),
        required=False,
        default=u"",
        description=_(
            u"Comments about this database item "
            u"[information entered below will not be "
            u"displayed on the public pages of "
            u"climate-adapt]"
        ),
    )

    origin_website = List(
        title=_(u"Item from third parties"),
        description=_(
            u"Used only to highlight items "
            u"provided by Third parties. "
            u"<br>Please don't compile "
            u"this field if you are a Climate-ADAPT expert "
            u"creating a new item."
        ),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.origin_website"),
    )

    logo = NamedBlobImage(
        title=_(u"Logo"),
        description=_(
            u"Upload a representative picture or logo for the item."
            u" Recommended size: at least 360/180 px, aspect ratio 2x"
        ),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u"Thumbnail"),
        description=_(
            u"Upload a representative picture or logo for the item. "
            u"Recommended size: at least 360/180 px, aspect ratio 2x. "
            u"This image will be used in the search result page - cards view. "
            u"If this image doesn't exist, then the logo image will be used."
        ),
        required=False,
    )

    contributor_list = RelationList(
        title=u"Contributor(s)",
        default=[],
        description=_(
            u"Select from the Climate ADAPT Organisation items the "
            u"organisations contributing to/ involved in this item"
        ),
        value_type=RelationChoice(
            title=_(u"Related"),
            vocabulary="eea.climateadapt.organisations"
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    # TODO: this will be a widget
    other_contributor = Text(
        title=_(u"Other contributor(s)"),
        required=False,
        default=u"",
        description=_(
            u"Please first verify if the contributor is "
            u"already part of the Climate ADAPT Database."
            u" If not, it is suggested to first create a "
            u"new Organisation item (%s). As last"
            u" alternative please add the new "
            u"contributor(s) in the following box, using "
            u"the official name" % ADD_ORGANISATION_URL
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
    directives.omitted(IEditForm, "rating")
    directives.omitted(IAddForm, "rating")
    # directives.omitted(IAddForm, "modification_date")
    # directives.omitted(IEditForm, "modification_date")
    # directives.omitted(IAddForm, "creation_date")
    # directives.omitted(IEditForm, "creation_date")
    # directives.omitted(IAddForm, "id")
    # directives.omitted(IEditForm, "id")
    # end

    implementation_type = Choice(
        title=_(u"Implementation Type"),
        required=False,
        default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype",
    )

    spatial_layer = TextLine(title=_(u"Spatial Layer"),
                             required=False, default=u"")

    spatial_values = List(
        title=_(u"Countries"),
        description=_(u"European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    # TODO: startdate, enddate, publicationdate have no values in DB
    # TODO: specialtagging is not used in any view jsp, only in add and edit
    # views

    form.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_(u"Adaptation approaches"),
        description=_(u"Select one or more approaches."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    measure_type = Choice(
        title=_(u"Measure Type"),
        required=True,
        default="A",
        vocabulary="eea.climateadapt.acemeasure_types",
    )

    health_impacts = List(
        title=_(u"Health impacts"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.health_impacts"),
    )

    include_in_observatory = Bool(
        title=_(u"Include in observatory"), required=False, default=False
    )

    include_in_mission = Bool(
        title=_(u"Include in the Mission Portal"), required=False, default=False
    )

    important = Bool(title=_(u"High importance"),
                     required=False, default=False)

    rating = Int(title=_(u"Rating"), required=True, default=0)

    special_tags = Tuple(
        title=_(u"Special tagging"),
        description=_(
            u"Used only by Climate-ADAPT administrator. Please don't "
            u"compile this field if you are a Climate-ADAPT expert creating a new "
            u"item."
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
        title=_(u"Date of item's creation"),
        description=u"The date refers to the moment in which the item "
        u"has been prepared or  updated by contributing "
        u"experts to be submitted for the publication in "
        u"Climate ADAPT."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u'add only the year, please select "day: 1", "month: January" '
        u"and then the year",
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
alsoProvides(IAceMeasure['implementation_type'], ILanguageIndependentField)
alsoProvides(IAceMeasure['important'], ILanguageIndependentField)
alsoProvides(IAceMeasure['measure_type'], ILanguageIndependentField)
alsoProvides(IAceMeasure['rating'], ILanguageIndependentField)
alsoProvides(IAceMeasure['spatial_layer'], ILanguageIndependentField)
alsoProvides(IAceMeasure['spatial_values'], ILanguageIndependentField)

from collective.geolocationbehavior.geolocation import IGeolocatable
alsoProvides(IGeolocatable['geolocation'], ILanguageIndependentField)
