from collective import dexteritytextindexer
from eea.climateadapt import MessageFactory as _
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implements
from zope.schema import Bool, Choice, Int, List, Text, TextLine
from z3c.form.interfaces import IEditForm


class IAceItem(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Item
    """

    dexteritytextindexer.searchable('long_description')

    form.fieldset('default',
        label=u'Item Description',
        fields=['title', 'long_description', 'keywords', 'sectors',
                'climate_impacts', 'elements', 'year']
    )

    form.fieldset('reference_information',
        label=u'Reference information',
        fields=['websites', 'source']
    )

    # TODO:
    # form.fieldset('reference_information',
    #     label=u'Documents',
    #     fields=[]
    # )

    form.fieldset('geographic_information',
        label=u'Geographic Information',
        fields=['geochars', 'comments']
    )

    form.fieldset('backend',
        label=u'Backend fields',
        fields=[]
    )

    # -----------[ "default" fields ]------------------

    title = TextLine(title=_(u"Title"),
                     description=u"Item Name (250 character limit)",
                     required=True)

    long_description = RichText(title=(u"Description"),
                                description=u"Provide a description of the item. (5,000 character limit)",
                                required=True)

    # TODO: "keyword" from SQL is Subject
    keywords = RichText(title=_(u"Keywords"),
                        description=_(u"Describe and tag this item with relevant keywords. Separate each keyword with a comma. For example, example keyword 1, example keyword 2 (1,000 character limit)"),
                        required=True)

    sectors = List(title=_(u"Sectors"),
                   description=_(u"Select one or more relevant sector policies that this item relates to."),
                   required=True,
                   value_type=Choice(
                       vocabulary="eea.climateadapt.aceitems_sectors",),
                   )

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Select one or more climate change impact topics that this item relates to."),
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

    year = Int(title=_(u"Year"), description=u"Date of publication/release/update of the item", required=False)

    # -----------[ "reference_information" fields ]------------------

    websites = RichText(title=_(u"Websites"),
                        description=u'List the Name and Website where the item can be found or is described. (500 character limit). Please separate each website with semicolon.',
                        required=False,)

    source = RichText(title=_(u"Source"),
                      required=False,
                      description=u"Describe the original source of the item description (250 character limit)")

    # -----------[ "geographic_information" fields ]------------------

    form.widget(geochars='eea.climateadapt.widgets.geochar.GeoCharFieldWidget')
    geochars = Text(title=_(u"Geographic characterisation"),
                    required=False,
                    default=u'{"geoElements":{"element":"GLOBAL","macrotrans":null,"biotrans":null,"countries":[],"subnational":[],"city":""}}',
                    description=u"Select the characterisation for this item",
                    )

    comments = Text(title=_(u"Comments"), required=False, default=u"",
                    description=u"Comments about this database item [information entered below will not be displayed on the public pages of climate-adapt]")

    # -----------[ "omitted" fields ]------------------
    directives.omitted(IEditForm, 'data_type', 'storage_type', 'spatial_layer',
                       'spatial_values', 'important', 'metadata',
                       'special_tags', 'rating')

    # -----------[ "backend" fields ]------------------

    # fix???
    data_type = Choice(title=_(u"Data Type"),
                       required=True,
                       vocabulary="eea.climateadapt.aceitems_datatypes")

    # fix???
    storage_type = Choice(title=_(u"Storage Type"),
                          required=True,
                          vocabulary="eea.climateadapt.aceitems_storagetypes")

    spatial_layer = TextLine(title=_(u"Spatial Layer"),
                             required=False,
                             default=u""
                             )

    spatial_values = List(title=_(u"Countries"),
                          description=_(u"European countries"),
                          required=False,
                          value_type=Choice(
                              vocabulary="eea.climateadapt.ace_countries"))

    important = Bool(title=_(u"High importance"), required=False,
                     default=False)

    # websites = List(title=_(u"Websites"),
    #                 required=True,
    #                 value_type=TextLine(title=_(u"Link"), ))
    metadata = RichText(title=_(u"Metadata"), required=False,)


    # # TODO: see if possible to use eea.promotions for this
    # featured = List(title=_(u"Featured in location"),
    #                 description=_(u"TODO: Featured description here"),
    #                 required=False,
    #                 value_type=Choice(
    #                     vocabulary="eea.climateadapt.aceitems_featured",),
    #                 )

    special_tags = List(title=_(u"Special tagging"),
                        required=False,
                        value_type=TextLine(title=_(u"Tag"))
                        )

    rating = Int(title=_(u"Rating"), required=True, default=0)

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


class IPublicationReport(IAceItem):
    """ Publication Report Interface
    """


class IInformationPortal(IAceItem):
    """ Information Portal Interface
    """


class IGuidanceDocument(IAceItem):
    """ Guidance Document Interface
    """


class ITool(IAceItem):
    """ Tool Interface
    """


class IOrganisation(IAceItem):
    """ Organisation Interface"""


class IIndicator(IAceItem):
    """ Indicator Interface"""


class IAction(IAceItem):
    """ Action Interface"""


class IMapGraphDataset(IAceItem):
    """ Maps, Graphs and Datasets Interface
    """


class IResearchProject(IAceItem):
    """ ResearchProject Interface
    """


class PublicationReport(dexterity.Item):
    implements(IPublicationReport)

    search_type = "DOCUMENT"


class InformationPortal(dexterity.Item):
    implements(IInformationPortal)

    search_type = "INFORMATIONSOURCE"


class GuidanceDocument(dexterity.Item):
    implements(IGuidanceDocument)

    search_type = "GUIDANCE"


class Tool(dexterity.Item):
    implements(ITool)

    search_type = "TOOL"


class Organisation(dexterity.Item):
    implements(IOrganisation)

    search_type = "ORGANISATION"


class Indicator(dexterity.Item):
    implements(IIndicator)

    search_type = "INDICATOR"


class MapGraphDataset(dexterity.Item):
    implements(IMapGraphDataset)

    search_type = "MAPGRAPHDATASET"


class ResearchProject(dexterity.Item):
    implements(IResearchProject)

    search_type = "RESEARCHPROJECT"


class Action(dexterity.Item):
    implements(IAction)

    search_type = "ACTION"
