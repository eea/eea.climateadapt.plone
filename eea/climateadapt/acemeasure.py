from collective import dexteritytextindexer
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.app.contenttypes.interfaces import IImage
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import dexterity, form
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.interface import implements
from zope.schema import URI, Bool, Choice, Decimal, Int, List, Text, TextLine


class IAceMeasure(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Measure
    """

    # def updateWidgets(self):
    #     super(IAceMeasure, self).updateWidgets()
    #     import pdb; pdb.set_trace()
    #     self.fieldset['default'].label = 'bla bla'
    #
    # model.fieldset(u"default", label="Default", fields=['title'])

    # updateWidgets(form)

    form.fieldset('default',
        label=u'Item Description',
        fields=['title', 'long_description', 'climate_impacts', 'keywords',
                'sectors', 'year']
    )

    form.fieldset('additional_details',
        label=u'Additional Details',
        fields=['stakeholder_participation', 'success_limitations',
                'cost_benefit', 'legal_aspects', 'implementation_time',
                'lifetime']
    )

    form.fieldset('reference_information',
        label=u'Reference information',
        fields=['websites', 'source']
    )

    # TODO:
    # form.fieldset('documents',
    #     label=u'Documents',
    #     fields=[]
    # )

    # TODO:
    # form.fieldset('reference_information',
    #     label=u'Documents',
    #     fields=[]
    # )

    form.fieldset('geographic_information',
        label=u'Geographic Information',
        fields=['geochars', 'comments']
    )

    # -----------[ "default" fields ]------------------

    title = TextLine(title=_(u"Title"),
                     description=_(u"Item Name (250 character limit)"),
                     required=True)
    dexteritytextindexer.searchable('long_description')
    long_description = RichText(title=_(u"Description"),
                                description=_(u"Brief Description:"),
                                required=True,)

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Select one or more climate change impact topics that this item relates to"),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",),
    )

    keywords = RichText(title=_(u"Keywords"),
                   description=_(u"Describe and tag this item with relevant keywords. Separate each keyword with a comma. For example, example keyword 1, example keyword 2 (1,000 character limit)"),
                   required=True,)

    sectors = List(title=_(u"Sectors"),
                   description=_(u"Select one or more relevant sector policies that this item relates to."),
                   required=True,
                   value_type=Choice(
                       vocabulary="eea.climateadapt.aceitems_sectors",),
                   )

    year = Int(title=_(u"Year"), description=u"Date of publication/release/update of the items related source", required=False,)

    # -----------[ "additional_details" fields ]------------------

    # category ???

    dexteritytextindexer.searchable('stakeholder_participation')
    stakeholder_participation = RichText(
        title=_(u"Stakeholder participation"), required=False,
        default=u"",
        description=_(u"Describe the Information about actors involved, the form of participation and the participation process. Focus should be on the level of participation needed and/or adopted already (from information, to full commitment in the deliberation/implementation process), with useful notes e.g. regarding motivations. (5,000 character limit)"))

    dexteritytextindexer.searchable('success_limitations')
    success_limitations = RichText(
        title=_(u"Success / limitations"), required=False, default=u"",
        description=_(u"Describe factors that are decisive for a successful implementation and expected challenges or limiting factors which may hinder the process and need to be considered (5,000 character limit)"))

    dexteritytextindexer.searchable('cost_benefit')
    cost_benefit = RichText(
        title=_(u"Cost / Benefit"), required=False, default=u"")

    dexteritytextindexer.searchable('legal_aspects')
    legal_aspects = RichText(title=_(u"Legal aspects"),
                             required=False,
                             default=u"",
                             description=_(u"Describe the Legislation framework from which the case originated, relevant institutional opportunities and constrains, which determined the case as it is (5000 character limit):"))

    dexteritytextindexer.searchable('implementation_time')
    implementation_time = RichText(
        title=_(u"Implementation Time"), required=False, default=None,
        description=_(u"Describe the time needed to implement the measure. Include: Time frame, e.g. 5-10 years, Brief explanation(250 char limit)"))

    dexteritytextindexer.searchable('lifetime')
    lifetime = RichText(title=_(u"Lifetime"),
                        required=False,
                        default=u"",
                        description=u"Describe the lifetime of the measure: Time frame, e.g. 5-10 years, Brief explanation(250 char limit)")

    # -----------[ "reference_information" fields ]------------------

    websites = List(title=_(u"Websites"),
                    description=_(u"List the Name and Website where the option can be found or is described. Note: may refer to the original document describing a measure and does not have to refer back to the project e.g. collected measures (500 character limit). Please separate each website with semicolon."),
                    required=False,
                    value_type=URI(title=_("A link"), required=False),
                    )

    dexteritytextindexer.searchable('source')
    source = RichText(title=_(u"Source"),
                      required=False,
                      description=_(u"Describe the original source (like name of a certain project) of the adaptation option description (250 character limit)"))

    # -----------[ "document" fields ]------------------

    # -----------[ "geographic_information" fields ]------------------

    # governance ???

    form.widget(geochars='eea.climateadapt.widgets.geochar.GeoCharFieldWidget')
    geochars = Text(
        title=_(u"Geographic characterization"),
        required=False, default=u"",
        description=_(u"Input the characterisation for this case study")
    )

    comments = Text(title=_(u"Comments"), required=False, default=u"",
                    description=_(u"Comments about this database item [information entered below will not be displayed on the public pages of climate-adapt]")
                    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IEditForm, 'implementation_type')
    directives.omitted(IAddForm, 'implementation_type')
    directives.omitted(IEditForm, 'challenges')
    directives.omitted(IAddForm, 'challenges')
    directives.omitted(IEditForm, 'spatial_layer')
    directives.omitted(IAddForm, 'spatial_layer')
    directives.omitted(IEditForm, 'spatial_values')
    directives.omitted(IAddForm, 'spatial_values')
    directives.omitted(IEditForm, 'contact')
    directives.omitted(IAddForm, 'contact')
    directives.omitted(IEditForm, 'elements')
    directives.omitted(IAddForm, 'elements')
    directives.omitted(IEditForm, 'measure_type')
    directives.omitted(IAddForm, 'measure_type')
    directives.omitted(IEditForm, 'important')
    directives.omitted(IAddForm, 'important')
    directives.omitted(IEditForm, 'rating')
    directives.omitted(IAddForm, 'rating')
    directives.omitted(IEditForm, 'objectives')
    directives.omitted(IAddForm, 'objectives')
    directives.omitted(IEditForm, 'solutions')
    directives.omitted(IAddForm, 'solutions')
    directives.omitted(IEditForm, 'adaptationoptions')
    directives.omitted(IAddForm, 'adaptationoptions')
    directives.omitted(IEditForm, 'relevance')
    directives.omitted(IAddForm, 'relevance')
    directives.omitted(IEditForm, 'primephoto')
    directives.omitted(IAddForm, 'primephoto')
    directives.omitted(IEditForm, 'supphotos')
    directives.omitted(IAddForm, 'supphotos')

    # end

    implementation_type = Choice(
        title=_(u"Implementation Type"), required=False, default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype"
    )

    dexteritytextindexer.searchable('challenges')
    challenges = RichText(
        title=_(u"Challenges"), required=False, default=None,
    )

    spatial_layer = TextLine(
        title=_(u"Spatial Layer"), required=False, default=u"")

    spatial_values = List(title=_(u"Countries"),
                          description=_(u"European countries"),
                          required=False,
                          value_type=Choice(
                              vocabulary="eea.climateadapt.ace_countries"))

    dexteritytextindexer.searchable('contact')
    contact = RichText(title=_(u"Contact"), required=False, default=u"")

    # keywords = List(title=_(u"Keywords"),
    #                description=_(u"Keywords related to the project"),
    #                required=False,
    #                value_type=TextLine(title=_(u"Tag"))
    # )

    # TODO: startdate, enddate, publicationdate have no values in DB
    # TODO: specialtagging is not used in any view jsp, only in add and edit
    # views

    elements = List(title=_(u"Elements"),
                    description=_(u"TODO: Elements description here"),
                    required=False,
                    value_type=Choice(
                        vocabulary="eea.climateadapt.aceitems_elements",),
                    )

    # TODO: special tagging implement as related

    measure_type = Choice(title=_(u"Measure Type"),
                          required=True,
                          default="A",
                          vocabulary="eea.climateadapt.acemeasure_types")

    important = Bool(title=_(u"High importance"), required=False,
                     default=False)

    rating = Int(title=_(u"Rating"), required=True, default=0)

    dexteritytextindexer.searchable('objectives')
    objectives = RichText(title=_(u"Objectives"), required=False, default=u"")

    dexteritytextindexer.searchable('solutions')
    solutions = RichText(title=_(u"Solutions"), required=False, default=u"")

    # dexteritytextindexer.searchable('summary')
    # summary = Text(title=_(u"Summary"), required=False, default=u"")

    adaptationoptions = List(
        title=_(u"Adaptation Options"),
        required=False,
        value_type=Int(),   # TODO:  leave it like that, until we figure it out
    )   # TODO: reimplement as list
    relevance = List(
        title=_(u"Relevance"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_relevance",),
        )
    primephoto = RelationChoice(
        title=_(u"Prime photo"),
        source=ObjPathSourceBinder(object_provides=IImage.__identifier__),
        required=False,
    )
    supphotos = RelationList(
        title=u"Gallery",
        default=[],
        value_type=RelationChoice(
            title=_(u"Related"),
            source=ObjPathSourceBinder(
                object_provides=IImage.__identifier__)
            ),
        required=False,
    )
    # approved is done by workflow

directives.widget('primephoto', AutocompleteFieldWidget)
directives.widget('supphotos', AutocompleteFieldWidget)


class ICaseStudy(IAceMeasure):
    """ Case study
    """
    # location - a clickable map, not provided if is "Adaptation option" type

    location_lat = Decimal(title=_(u"Location latitude"), required=True)
    location_lon = Decimal(title=_(u"Location longitude"), required=True)


class IAdaptationOption(IAceMeasure):
    """ Adaptation Option
    """


class CaseStudy(dexterity.Container):
    implements(ICaseStudy, IClimateAdaptContent)

    search_type = "ACTION"


class AdaptationOption(dexterity.Container):
    implements(IAdaptationOption, IClimateAdaptContent)

    search_type = "MEASURE"


# class AceMeasure(Base):
#     __tablename__ = 'ace_measure'
#
#     measureid = Column(
#         BigInteger,
#         primary_key=True,
#         server_default=text("nextval('ace_measure_id_seq'::regclass)"))
#     companyid = Column(BigInteger)
#     groupid = Column(BigInteger)
#     name = Column(String(255))
#     description = Column(Text)
#     implementationtype = Column(Text)
#     implementationtime = Column(String(255))
#     lifetime = Column(Text)
#     spatiallayer = Column(Text)
#     spatialvalues = Column(Text)
#     legalaspects = Column(Text)
#     stakeholderparticipation = Column(Text)
#     contact = Column(Text)
#     succeslimitations = Column(Text)
#     website = Column(Text)
#     costbenefit = Column(Text)
#     keywords = Column(Text)
#     startdate = Column(DateTime)
#     enddate = Column(DateTime)
#     publicationdate = Column(DateTime)
#     specialtagging = Column(
#         String(75),
#         server_default=text("NULL::character varying"))
#     sectors_ = Column(String(255))
#     elements_ = Column(String(255))
#     climateimpacts_ = Column(String(255))
#     mao_type = Column(String(24))
#     source = Column(Text)
#     rating = Column(BigInteger)
#     importance = Column(BigInteger)
#     lon = Column(Float(53))
#     lat = Column(Float(53))
#     satarea = Column(String(254))
#     controlstatus = Column(SmallInteger)
#     creator = Column(String(75))
#     creationdate = Column(DateTime)
#     moderator = Column(String(2000))
#     approvaldate = Column(DateTime)
#     replacesid = Column(BigInteger)
#     comments = Column(Text)
#     textwebpage = Column(Text)
#     admincomment = Column(Text)
#     casestudyfeature = Column(String(50))
#     objectives = Column(Text)
#     challenges = Column(Text)
#     adaptationoptions = Column(String(2500))
#     solutions = Column(Text)
#     relevance = Column(String(2500))
#     primephoto = Column(String(10))
#     supphotos = Column(String(50))
#     supdocs = Column(String(50))
#     year = Column(String(7))
#     geos_ = Column(String(250))
#     geochars = Column(Text)
#     category = Column(String(50))
#     lockdate = Column(DateTime)
#
