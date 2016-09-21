from collective import dexteritytextindexer
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from eea.climateadapt.widgets.ajaxselect import BetterAjaxSelectWidget
from plone.app.textfield import RichText
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.autoform import directives
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm, IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.interface import implementer, implements
from zope.schema import URI, Bool, Choice, Int, List, Text, TextLine, Tuple


class IAceProject(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Project
    """

    dexteritytextindexer.searchable('acronym')
    dexteritytextindexer.searchable('title')
    dexteritytextindexer.searchable('lead')
    dexteritytextindexer.searchable('partners')
    dexteritytextindexer.searchable('keywords')
    dexteritytextindexer.searchable('sectors')
    dexteritytextindexer.searchable('climate_impacts')
    dexteritytextindexer.searchable('elements')
    dexteritytextindexer.searchable('funding')
    dexteritytextindexer.searchable('duration')

    dexteritytextindexer.searchable('websites')
    dexteritytextindexer.searchable('source')

    dexteritytextindexer.searchable('geochars')

    dexteritytextindexer.searchable('specialtagging')
    dexteritytextindexer.searchable('special_tags')
    dexteritytextindexer.searchable('important')
    dexteritytextindexer.searchable('spatial_layer')
    dexteritytextindexer.searchable('spatial_values')

    form.fieldset('default',
                  label=u'Item Description',
                  fields=['acronym', 'title', 'lead', 'long_description',
                          'partners', 'keywords', 'sectors', 'climate_impacts',
                          'elements', 'funding', 'duration', 'featured'])

    form.fieldset('reference_information',
                  label=u'Reference information',
                  fields=['websites', 'source'])

    form.fieldset('geographic_information',
                  label=u'Geographic Information',
                  fields=['geochars', 'comments'])

    form.fieldset('categorization',
                  label=u'Categorization',
                  fields=['special_tags']
                  )

    # -----------[ "default" fields ]------------------


    # These fields are richtext in the db:
    #set(['keywords', 'partners', 'admincomment', 'abstracts', 'source'])

    acronym = TextLine(title=_(u"Acronym"),
                       description=_(u"Acronym of the project"),
                       required=True,
                       )

    title = TextLine(title=_(u"Title"),
                     description=_(u"Project title or name"),
                     required=True,
                     )

    dexteritytextindexer.searchable('long_description')
    long_description = RichText(
        title=_(u"Abstracts"),
        description=_(u"Provide information focusing on project output. "
                      u"Possibly on specific Website features."),
        required=True,
    )

    lead = TextLine(
        title=_(u"Lead"),
        description=_(u"Lead organisation or individual of the project"),
        required=True,
    )

    dexteritytextindexer.searchable('partners')
    partners = RichText(
        title=_(u"Partners"),
        description=_(u"Provide information about project partners "
                      u"(organisation names)."),
        required=True,
    )

    dexteritytextindexer.searchable('keywords')
    keywords = Tuple(
        title=_(u"Keywords"),
        description=_(u"Provide Keywords related to the project. "
                      u"Press Enter after writing your keyword."),
        required=False,
        value_type=TextLine(),
        missing_value=(None),
    )

    sectors = List(
        title=_(u"Sectors"),
        description=_(u"Select one or more relevant sector policies that "
                      u"this item relates to."),
        required=True,
        missing_value=[],
        default=None,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",),
    )

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Select one or more climate change impact topics that "
                      u"this item relates to."),
        missing_value=[],
        default=None,
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",),
    )

    elements = List(title=_(u"Elements"),
                    description=_(u"Select one or more elements."),
                    required=False,
                    value_type=Choice(
                        vocabulary="eea.climateadapt.aceitems_elements",),
                    )

    funding = TextLine(title=_(u"Funding"),
                       description=_(u"Provide source of funding"),
                       required=False,
                       )

    duration = TextLine(
        title=_(u"Duration"),
        description=_(u"Provide duration of project - Start and end date [yr]"),
        required=False,
    )

    featured = Bool(title=_(u"Featured"),
                     required=False,
                     default=False,
                     )

    # -----------[ "reference_information" fields ]------------------
    directives.widget('websites', TextLinesWidget)
    websites = Tuple(
        title=_(u"Website"),
        description=_(u"List the Website where the item can be found or is "
                      u"described. Please place each website on a new line"),
        required=False,
        value_type=URI(),
        missing_value=(),
    )

    dexteritytextindexer.searchable('source')
    source = RichText(
        title=_(u"Source"),
        description=_(u"Provide source from which project was retrieved (e.g. "
                      u"specific DB) "),
        required=False)

    # -----------[ "geographic_information" fields ]------------------
    form.widget(geochars='eea.climateadapt.widgets.geochar.GeoCharFieldWidget')
    geochars = Text(
        title=_(u"Geographic characterization"),
        description=_(u"Select the characterisation for this project"),
        required=True,
    )

    comments = Text(
        title=_(u"Source"),
        description=_(u"Comments about this database item [information entered"
                      u" below will not be displayed on the public pages of "
                      u"climate-adapt]"),
        required=False,
    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IEditForm, 'specialtagging')
    directives.omitted(IAddForm, 'specialtagging')
    # directives.omitted(IEditForm, 'special_tags')
    # directives.omitted(IAddForm, 'special_tags')
    directives.omitted(IEditForm, 'important')
    directives.omitted(IAddForm, 'important')
    directives.omitted(IEditForm, 'rating')
    directives.omitted(IAddForm, 'rating')
    directives.omitted(IEditForm, 'spatial_layer')
    directives.omitted(IAddForm, 'spatial_layer')
    directives.omitted(IEditForm, 'spatial_values')
    directives.omitted(IAddForm, 'spatial_values')
    # end

    specialtagging = TextLine(
        title=_(u"Special Tagging"),
        description=_(u"Special tags that allow for linking the item"),
        required=False,
        )

    # special_tags = TextLine(
    #     title=_(u"Special Tagging"),
    #     description=_(u"Special tags that allow for linking the item"),
    #     required=False,
    #     )

    special_tags = Tuple(
        title=_(u"Special tagging"),
        required=False,
        value_type=TextLine(),
        missing_value=(None),
    )

    important = Bool(title=_(u"Important"),
                     required=False,
                     default=False,
                     )

    rating = Int(title=_(u"Rating"), required=True, default=0)

    spatial_layer = TextLine(
        title=_(u"Spatial Layer"), required=False, default=u"",
        )

    spatial_values = List(title=_(u"Countries"),
                          description=_(u"European countries"),
                          required=False,
                          value_type=Choice(
                              vocabulary="eea.climateadapt.ace_countries"),
                          )


class AceProject(dexterity.Container):
    implements(IAceProject, IClimateAdaptContent)

    search_type = "RESEARCHPROJECT"


@adapter(getSpecification(IAceProject['keywords']), IWidgetsLayer)
@implementer(IFieldWidget)
def KeywordsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = 'eea.climateadapt.keywords'
    return widget


@adapter(getSpecification(IAceProject['special_tags']), IWidgetsLayer)
@implementer(IFieldWidget)
def SpecialTagsFieldWidget(field, request):
    widget = FieldWidget(field, BetterAjaxSelectWidget(request))
    widget.vocabulary = 'eea.climateadapt.special_tags'
    return widget
