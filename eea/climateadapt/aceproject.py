from collective import dexteritytextindexer
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.interfaces import IEditForm, IAddForm
from zope.interface import implements
from zope.schema import Bool, Choice, Int, List, Text, TextLine, Tuple, URI


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

    dexteritytextindexer.searchable('specialtagging')
    dexteritytextindexer.searchable('important')
    dexteritytextindexer.searchable('spatial_layer')
    dexteritytextindexer.searchable('spatial_values')

    form.fieldset('default',
                  label=u'Item Description',
                  fields=['acronym', 'title', 'lead', 'long_description',
                          'partners', 'keywords', 'sectors', 'climate_impacts',
                          'elements', 'funding', 'duration'])

    form.fieldset('reference_information',
                  label=u'Reference information',
                  fields=['websites', 'source'])

    form.fieldset('geographic_information',
                  label=u'Geographic Information',
                  fields=['geochars', 'comments'])

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
        description=_(u"Provide Keywords related to the project."),
        required=True,
        value_type=TextLine(),
        missing_value=(),
    )

    sectors = List(
        title=_(u"Sectors"),
        description=_(u"Select one or more relevant sector policies that "
                      u"this item relates to."),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_sectors",),
    )

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Select one or more climate change impact topics that "
                      u"this item relates to."),
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

    # -----------[ "reference_information" fields ]------------------
    websites = Tuple(
        title=_(u"Website"),
        description=_(u"List the Website where the item can be found or is "
                      u"described. Please place each website on a new line"),
        required=True,
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
