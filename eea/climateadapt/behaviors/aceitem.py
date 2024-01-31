from collective import dexteritytextindexer
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.schema import AbsoluteUrl, Uploader
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
from zope.interface import alsoProvides, implementer
from zope.schema import URI, Bool, Choice, Date, List, Text, TextLine, Tuple

# , Year, PortalType,


class IAceItem(IImageScaleTraversable):
    """
    Defines content-type schema for Ace Item
    """

    dexteritytextindexer.searchable("title")
    dexteritytextindexer.searchable("long_description")
    dexteritytextindexer.searchable("description")
    dexteritytextindexer.searchable("keywords")
    dexteritytextindexer.searchable("sectors")
    dexteritytextindexer.searchable("climate_impacts")
    dexteritytextindexer.searchable("elements")
    # dexteritytextindexer.searchable('year')

    dexteritytextindexer.searchable("websites")
    dexteritytextindexer.searchable("source")

    dexteritytextindexer.searchable("geochars")

    dexteritytextindexer.searchable("data_type")
    dexteritytextindexer.searchable("storage_type")
    dexteritytextindexer.searchable("spatial_layer")
    dexteritytextindexer.searchable("spatial_values")
    dexteritytextindexer.searchable("important")
    dexteritytextindexer.searchable("metadata")
    dexteritytextindexer.searchable("special_tags")

    # directives.omitted(IAddForm, 'relatedItems')
    # directives.omitted(IEditForm, 'relatedItems')

    form.fieldset(
        "default",
        label=u"Item Description",
        fields=[
            "title",
            "description",
            "long_description",
            "keywords",
            "sectors",
            "climate_impacts",
            "elements",
            "featured",
        ],
    )

    form.fieldset(
        "reference_information",
        label=u"Reference information",
        fields=["websites", "source", "special_tags", "comments"],
    )

    form.fieldset(
        "geographic_information", label=u"Geographic Information", fields=["geochars"]
    )

    form.fieldset(
        "categorization",
        label=u"Inclusion in the subsites",
        fields=["include_in_observatory",
                "include_in_mission", "health_impacts"],
    )

    # form.fieldset('inclusion_health_observatory',
    #              label=u'Inclusion in the Health Observatory',
    #              fields=['health_impacts', 'include_in_observatory']
    #              )

    form.fieldset("backend", label=u"Backend fields", fields=[])

    # -----------[ "default" fields ]------------------
    # these are the richtext fields from the db:
    # set(['description', 'storedat', 'admincomment', 'comments', 'source',
    #      'keyword', 'textsearch'])

    origin_website = List(
        title=_(u"Item from third parties"),
        description=_(
            u"Used only to highlight items "
            u"provided by Third parties."
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

    title = TextLine(
        title=_(u"Title"), description=u"Item Name (250 character limit)", required=True
    )

    long_description = RichText(
        title=(u"Description"),
        description=u"Provide a description of the " u"item.(5,000 character limit)",
        required=True,
    )

    description = Text(
        title=_(u"Short summary"),
        required=False,
        description=u"Enter a short summary that will be used in listings.",
        missing_value=u'',
    )

    keywords = Tuple(
        title=_(u"Keywords"),
        description=_(
            u"Describe and tag this item with relevant keywords."
            u"Press Enter after writing your keyword."
        ),
        required=False,
        value_type=TextLine(),
        missing_value=None,
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(
        title=_(u"Sectors"),
        description=_(
            u"Select one or more relevant sector policies"
            u" that this item relates to."
        ),
        required=True,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",
        ),
    )

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(
            u"Select one or more climate change impact topics that "
            u"this item relates to."
        ),
        required=True,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",
        ),
    )

    form.widget(elements="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    elements = List(
        title=_(u"Adaptation elements"),
        description=_(u"Select one or more elements."),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_elements",
        ),
    )

    # year = Year(title=_(u"Year"),
    #             description=u"Date of publication/release/update of the item",
    #             required=False
    #             )

    publication_date = Date(
        title=_(u"Date of item's creation"),
        description=u"The date refers to the moment in which the item "
        u"has been prepared by contributing experts to be "
        u"submitted for the publication in Climate "
        u"ADAPT Publication/last update date."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u'add only the year, please select "day: 1", "month: January" '
        u"and then the year",
        required=True,
    )

    featured = Bool(
        title=_(u"Featured"),
        required=False,
        default=False,
    )

    # -----------[ "reference_information" fields ]------------------

    directives.widget("websites", TextLinesWidget)
    websites = Tuple(
        title=_(u"Websites"),
        description=_(
            u"List the Websites where the item can be found or is "
            u"described. Please place each website on a new line"
        ),
        required=False,
        value_type=URI(),
        # missing_value=None,
    )

    source = RichText(
        title=_(u"References"),
        required=False,
        description=_(
            u"Describe the references (projects, a tools reports, etc.) "
            u"related to this item, providing further information about "
            u"it or its source."
        ),
    )

    # -----------[ "geographic_information" fields ]------------------

    form.widget(geochars="eea.climateadapt.widgets.geochar.GeoCharFieldWidget")
    geochars = Text(
        title=_(u"Geographic characterisation"),
        required=True,
        default=u'{"geoElements":{"element":"GLOBAL", "macrotrans"'
        u':null,"biotrans":null,"countries":[],'
        u'"subnational":[],"city":""}}',
        description=u"Select the characterisation for this item",
    )

    comments = Text(
        title=_(u"Comments"),
        required=False,
        default=u"",
        description=u"Comments about this database item "
        u"[information entered below will not be "
        u"displayed on the public pages of "
        u"climate-adapt]",
    )

    contributor_list = RelationList(
        title=u"Contributor(s)",
        default=[],
        description=_(
            u'Select from the Climate ADAPT "Organisation" items'
            u" the organisations contributing to/ involved in this"
            u" item"
        ),
        value_type=RelationChoice(
            title=_(u"Related"),
            vocabulary="eea.climateadapt.organisations"
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    other_contributor = Text(
        title=_(u"Other contributor(s)"),
        required=False,
        default=u"",
        description=_(
            u"Please first verify if the contributor is "
            u"already part of the Climate ADAPT Database."
            u" If not, it is suggested to first create a "
            u"new Organisation item "
            u"(<a target='_blank' "
            u"href='/metadata/organisations/++add++eea.climateadapt.organisation'>click here</a>). "
            u"As last alternative please add the new "
            u"contributor(s) in the following box, using "
            u"the official name"
        ),
    )

    # -----------[ "omitted" fields ]------------------
    # directives.omitted(IAddForm, "portal_type")
    # directives.omitted(IEditForm, "portal_type")

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

    directives.omitted(IAddForm, "important")
    directives.omitted(IEditForm, "important")

    directives.omitted(IAddForm, "metadata")
    directives.omitted(IEditForm, "metadata")

    directives.omitted(IAddForm, "rating")
    directives.omitted(IEditForm, "rating")

    # directives.omitted(IAddForm, 'special_tags')
    # directives.omitted(IEditForm, 'special_tags')

    # directives.omitted(IAddForm, "modification_date")
    # directives.omitted(IEditForm, "modification_date")
    #
    # directives.omitted(IAddForm, "creation_date")
    # directives.omitted(IEditForm, "creation_date")
    #
    # directives.omitted(IAddForm, "id")
    # directives.omitted(IEditForm, "id")

    # -----------[ "backend" fields ]------------------

    special_tags = Tuple(
        title=_(u"Special tagging"),
        description=_(
            u"Used only by Climate-ADAPT administrator. Please don't "
            u"compile this field if you are a Climate-ADAPT expert creating a new "
            u"item."
        ),
        required=False,
        value_type=TextLine(),
        missing_value=None,
    )

    # portal_type = PortalType(title=_(u"Portal type"),
    #                          required=False, default=u"")

    item_link = AbsoluteUrl(title=_(u"Item link"), required=False, default=u"")

    uploader = Uploader(title=_(u"Uploaded by"), required=False, default=u"")
    # fix???
    data_type = Choice(
        title=_(u"Data Type"),
        required=False,
        vocabulary="eea.climateadapt.aceitems_datatypes",
    )

    # fix???
    storage_type = Choice(
        title=_(u"Storage Type"),
        required=False,
        vocabulary="eea.climateadapt.aceitems_storagetypes",
    )

    spatial_layer = TextLine(title=_(u"Spatial Layer"),
                             required=False, default=u"")

    spatial_values = List(
        title=_(u"Countries"),
        description=_(u"European countries"),
        required=False,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    important = Bool(title=_(u"High importance"),
                     required=False, default=False)

    metadata = TextLine(
        title=_(u"Metadata"),
        required=False,
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
    # id = ASCIILine(
    #     title=_(u"Object ID"),
    #     required=False,
    # )

    # TODO: see if possible to use eea.promotions for this
    # featured = List(title=_(u"Featured in location"),
    #                 description=_(u"TODO: Featured description here"),
    #                 required=False,
    #                 value_type=Choice(
    #                     vocabulary="eea.climateadapt.aceitems_featured",),
    #                 )

    # rating = Int(title=_(u"Rating"), required=True, default=0)

    # TODO: rating??? seems to be manually assigned, not computed

    # TODO: storedat: can contain a related measure or project, or a URL
    # if contains inner contents, starts with ace_project_id=<id>
    # or ace_measure_id=<id>

    # supdocs - this is a related field. It seems to point to dlfileentry

    # replacesid - tot un related??

    # scenario: only 3 items have a value: "SCENES SUE", "SCENES ECF", "IPCCS",
    # IPCCSRES A1B
    # the options are stored in a AceItemScenario constant in Java code

    # TODO: special search behaviour, should aggregate most fields


@adapter(getSpecification(IAceItem["special_tags"]), IWidgetsLayer)
@implementer(IFieldWidget)
def SpecialTagsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = "eea.climateadapt.special_tags"

    return widget


@adapter(getSpecification(IAceItem["keywords"]), IWidgetsLayer)
@implementer(IFieldWidget)
def KeywordsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = "eea.climateadapt.keywords"
    # widget.vocabulary = 'plone.app.vocabularies.Catalog'

    return widget


alsoProvides(IAceItem['climate_impacts'], ILanguageIndependentField)
alsoProvides(IAceItem['comments'], ILanguageIndependentField)
alsoProvides(IAceItem['contributor_list'], ILanguageIndependentField)
alsoProvides(IAceItem['data_type'], ILanguageIndependentField)
alsoProvides(IAceItem['elements'], ILanguageIndependentField)
alsoProvides(IAceItem['featured'], ILanguageIndependentField)
alsoProvides(IAceItem['geochars'], ILanguageIndependentField)
alsoProvides(IAceItem['health_impacts'], ILanguageIndependentField)
alsoProvides(IAceItem['image'], ILanguageIndependentField)
alsoProvides(IAceItem['important'], ILanguageIndependentField)
alsoProvides(IAceItem['include_in_mission'], ILanguageIndependentField)
alsoProvides(IAceItem['include_in_observatory'], ILanguageIndependentField)
alsoProvides(IAceItem['item_link'], ILanguageIndependentField)
alsoProvides(IAceItem['keywords'], ILanguageIndependentField)
alsoProvides(IAceItem['logo'], ILanguageIndependentField)
alsoProvides(IAceItem['metadata'], ILanguageIndependentField)
alsoProvides(IAceItem['origin_website'], ILanguageIndependentField)
alsoProvides(IAceItem['other_contributor'], ILanguageIndependentField)
alsoProvides(IAceItem['publication_date'], ILanguageIndependentField)
alsoProvides(IAceItem['sectors'], ILanguageIndependentField)
alsoProvides(IAceItem['spatial_values'], ILanguageIndependentField)
alsoProvides(IAceItem['special_tags'], ILanguageIndependentField)
alsoProvides(IAceItem['storage_type'], ILanguageIndependentField)
alsoProvides(IAceItem['uploader'], ILanguageIndependentField)
alsoProvides(IAceItem['websites'], ILanguageIndependentField)
alsoProvides(IAceItem['spatial_layer'], ILanguageIndependentField)

from plone.app.dexterity.behaviors.metadata import IPublication

alsoProvides(IPublication['effective'], ILanguageIndependentField)
alsoProvides(IPublication['expires'], ILanguageIndependentField)
