#from plone.namedfile.field import NamedBlobFile
from collective import dexteritytextindexer
from collective.geolocationbehavior.geolocation import IGeolocatable
from eea.climateadapt import MessageFactory as _
from eea.climateadapt.interfaces import IClimateAdaptContent
from plone.app.contenttypes.interfaces import IImage
from plone.app.textfield import RichText
from plone.app.widgets.dx import AjaxSelectWidget
from plone.app.widgets.dx import RelatedItemsWidget
from plone.app.widgets.interfaces import IWidgetsLayer
from plone.autoform import directives
from plone.directives import dexterity, form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.form.browser.textlines import TextLinesWidget
from z3c.form.interfaces import IAddForm, IEditForm, IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from z3c.relationfield.schema import RelationChoice, RelationList
from zope.component import adapter
from zope.interface import implementer, implements
from zope.schema import List, Text, TextLine, Tuple
from zope.schema import URI, Bool, Choice, Int


class IAceMeasure(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Measure
    """

    dexteritytextindexer.searchable('title')
    dexteritytextindexer.searchable('long_description')
    dexteritytextindexer.searchable('climate_impacts')
    dexteritytextindexer.searchable('keywords')
    dexteritytextindexer.searchable('sectors')
    dexteritytextindexer.searchable('year')

    dexteritytextindexer.searchable('stakeholder_participation')
    dexteritytextindexer.searchable('success_limitations')
    dexteritytextindexer.searchable('cost_benefit')
    dexteritytextindexer.searchable('legal_aspects')
    dexteritytextindexer.searchable('implementation_time')
    dexteritytextindexer.searchable('lifetime')

    dexteritytextindexer.searchable('websites')
    dexteritytextindexer.searchable('source')

    dexteritytextindexer.searchable('geochars')

    dexteritytextindexer.searchable('implementation_type')
    dexteritytextindexer.searchable('challenges')
    dexteritytextindexer.searchable('spatial_layer')
    dexteritytextindexer.searchable('spatial_values')
    dexteritytextindexer.searchable('contact')
    dexteritytextindexer.searchable('measure_type')
    dexteritytextindexer.searchable('important')
    dexteritytextindexer.searchable('objectives')
    dexteritytextindexer.searchable('solutions')

    form.fieldset('default',
                  label=u'Item Description',
                  fields=['title', 'long_description', 'climate_impacts',
                          'challenges', 'objectives', #'adaptationoptions',
                          'solutions', 'relevance', 'keywords', 'sectors',
                          'year']
                  )

    form.fieldset('additional_details',
                  label=u'Additional Details',
                  fields=['category', 'stakeholder_participation',
                          'success_limitations',
                          'cost_benefit', 'legal_aspects',
                          'implementation_time', 'lifetime']
                  )

    form.fieldset('reference_information',
                  label=u'Reference information',
                  fields=['contact', 'websites', 'source']
                  )

# richtext fields in database:
# set(['legalaspects', 'implementationtime', 'description', 'source',
# 'objectives', 'stakeholderparticipation', 'admincomment', 'comments',
# 'challenges', 'keywords', 'contact', 'solutions', 'costbenefit',
# 'succeslimitations', 'lifetime'])

    form.fieldset('geographic_information',
                  label=u'Geographic Information',
                  fields=['governance_level', 'geochars', 'comments']
                  )

    # -----------[ "default" fields ]------------------

    title = TextLine(title=_(u"Title"),
                     description=_(u"Item Name (250 character limit)"),
                     required=True)

    dexteritytextindexer.searchable('long_description')
    long_description = RichText(title=_(u"Description"),
                                description=_(u"Brief Description:"),
                                required=True,)

    form.widget(climate_impacts="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Select one or more climate change impact topics that "
                      u"this item relates to"),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",),
    )

    challenges = RichText(
        title=_(u"Challenges"), required=True, default=None,
    )

    objectives = RichText(
        title=_(u"Objectives"), required=True, default=None,
    )

    solutions = RichText(
        title=_(u"Solutions"), required=True, default=None,
    )

    form.widget(relevance="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    relevance = List(
        title=_(u"Relevance"),
        required=True,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_relevance",),
    )

    keywords = Tuple(
        title=_(u"Keywords"),
        description=_(u"Describe and tag this item with relevant keywords. "
                      u"Press Enter after writing your keyword."),
        required=False,
        value_type=TextLine(),
        missing_value=(None),
    )

    form.widget(sectors="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    sectors = List(title=_(u"Sectors"),
                   description=_(u"Select one or more relevant sector policies"
                                 u" that this item relates to."),
                   required=True,
                   value_type=Choice(
                       vocabulary="eea.climateadapt.aceitems_sectors",),
                   )

    year = Int(title=_(u"Year"),
               description=u"Date of publication/release/update of the items "
                           u"related source",
               required=False,)

    # -----------[ "additional_details" fields ]------------------

    form.widget(category="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    category = List(
        title=_(u"Category"),
        description=_(u"Select one or more categories of adaptation options: "
                      u"The 3 options are:"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_category",),
    )

    dexteritytextindexer.searchable('stakeholder_participation')
    stakeholder_participation = RichText(
        title=_(u"Stakeholder participation"), required=False,
        default=u"",
        description=_(u"Describe the Information about actors involved, the "
                      u"form of participation and the participation process. "
                      u" Focus should be on the level of participation needed "
                      u"and/or adopted already (from information, to full "
                      u"commitment in the deliberation/implementation "
                      u"process), with useful notes e.g. regarding "
                      u"motivations. (5,000 character limit)"))

    dexteritytextindexer.searchable('success_limitations')
    success_limitations = RichText(
        title=_(u"Success / limitations"), required=False, default=u"",
        description=_(u"Describe factors that are decisive for a successful "
                      u"implementation and expected challenges or limiting "
                      u"factors which may hinder the process and need to be "
                      u"considered (5,000 character limit)"))

    dexteritytextindexer.searchable('cost_benefit')
    cost_benefit = RichText(
        title=_(u"Cost / Benefit"), required=False, default=u"")

    dexteritytextindexer.searchable('legal_aspects')
    legal_aspects = RichText(title=_(u"Legal aspects"),
                             required=False,
                             default=u"",
                             description=_(u"Describe the Legislation "
                                           u"framework from which the case "
                                           u"originated, relevant institutional"
                                           u" opportunities and constrains, "
                                           u"which determined the case as it "
                                           u"is (5000 character limit):"))

    dexteritytextindexer.searchable('implementation_time')
    implementation_time = RichText(
        title=_(u"Implementation Time"), required=False, default=None,
        description=_(u"Describe the time needed to implement the measure. "
                      u"Include: Time frame, e.g. 5-10 years, Brief "
                      u"explanation(250 char limit)"))

    dexteritytextindexer.searchable('lifetime')
    lifetime = RichText(title=_(u"Lifetime"),
                        required=False,
                        default=u"",
                        description=u"Describe the lifetime of the measure: "
                        u"Time frame, e.g. 5-10 years, Brief explanation "
                        u"(250 char limit)")

    # -----------[ "reference_information" fields ]------------------

    contact = RichText(
        title=_(u"Contact"), required=True, default=u"",
        description=_(u"Contact of reference (institution and persons) who is "
                      u"directly involved in the development and "
                      u"implementation of the case. (500 char limit) "))

    directives.widget('websites', TextLinesWidget)
    websites = Tuple(
        title=_(u"Website"),
        description=_(u"List the Website where the option can be found"
                      u" or is described. Note: may refer to the original "
                      u"document describing a measure and does not have to "
                      u"refer back to the project e.g. collected measures."),
        required=True,
        value_type=URI(),
        missing_value=(),
    )

    dexteritytextindexer.searchable('source')
    source = RichText(title=_(u"Source"),
                      required=False,
                      description=_(u"Describe the original source (like name "
                                    u"of a certain project) of the adaptation "
                                    u"option description (250 character limit)"
                                    ))

    # -----------[ "document" fields ]------------------

    # -----------[ "geographic_information" fields ]------------------

    form.widget(governance_level="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    governance_level = List(
        title=_(u"Governance Level"),
        description=_(u"Select the one governance level that relates to this "
                      u"adaptation option"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_governancelevel",),
    )

    form.widget(geochars='eea.climateadapt.widgets.geochar.GeoCharFieldWidget')
    geochars = Text(
        title=_(u"Geographic characterization"),
        required=True, default=u"",
        description=_(u"Input the characterisation for this case study")
    )

    comments = Text(title=_(u"Comments"), required=False, default=u"",
                    description=_(u"Comments about this database item "
                                  u"[information entered below will not be "
                                  u"displayed on the public pages of "
                                  u"climate-adapt]")
                    )

    # -----------[ "omitted" fields ]------------------

    directives.omitted(IEditForm, 'implementation_type')
    directives.omitted(IAddForm, 'implementation_type')
    directives.omitted(IEditForm, 'spatial_layer')
    directives.omitted(IAddForm, 'spatial_layer')
    directives.omitted(IEditForm, 'spatial_values')
    directives.omitted(IAddForm, 'spatial_values')
    directives.omitted(IEditForm, 'elements')
    directives.omitted(IAddForm, 'elements')
    directives.omitted(IEditForm, 'measure_type')
    directives.omitted(IAddForm, 'measure_type')
    directives.omitted(IEditForm, 'important')
    directives.omitted(IAddForm, 'important')
    directives.omitted(IEditForm, 'rating')
    directives.omitted(IAddForm, 'rating')

    # end

    implementation_type = Choice(
        title=_(u"Implementation Type"), required=False, default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype"
    )

    spatial_layer = TextLine(
        title=_(u"Spatial Layer"), required=False, default=u"")

    spatial_values = List(title=_(u"Countries"),
                          description=_(u"European countries"),
                          required=False,
                          value_type=Choice(
                              vocabulary="eea.climateadapt.ace_countries"))

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

    # dexteritytextindexer.searchable('summary')
    # summary = Text(title=_(u"Summary"), required=False, default=u"")


class IAdaptationOption(IAceMeasure):
    """ Adaptation Option
    """


class ICaseStudy(IAceMeasure):  #, IGeolocatable):
    """ Case study
    """

    # form.fieldset('additional_detailsdefault',
    #               label=u'Additional details',
    #               fields=['adaptationoptions', 'geolocation']
    #               )

    # form.fieldset('documents',
    #               label=u'Illustrations and Documents',
    #               fields=['primary_photo']
    #               )

    directives.omitted(IEditForm, 'primephoto')
    directives.omitted(IAddForm, 'primephoto')
    directives.omitted(IEditForm, 'supphotos')
    directives.omitted(IAddForm, 'supphotos')

    # form.widget(adaptationoptions=RelatedItemsFieldWidget)
    adaptationoptions = RelationList(
        title=u"Adaptation Options",
        default=[],
        value_type=RelationChoice(
            title=_(u"Related"),
            source=ObjPathSourceBinder(
                #object_provides=IAdaptationOption.__identifier__
                portal_type='eea.climateadapt.adaptationoption',
                path={'/Plone/metadata/adaptation-options/'},
            )
        ),
        required=False,
    )

    primary_photo = NamedBlobImage(
        title=_(u"Primary photo"),
        required=False,
    )

    # BBB fields, only used during migration
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


@adapter(getSpecification(ICaseStudy['adaptationoptions']), IWidgetsLayer)
@implementer(IFieldWidget)
def AdaptationOptionsFieldWidget(field, request):
    widget = FieldWidget(field, RelatedItemsWidget(request))
    widget.vocabulary = 'plone.app.vocabularies.Catalog'
    #widget.vocabulary = 'eea.climateadapt.adaptation_options'
    return widget


class CaseStudy(dexterity.Container):
    implements(ICaseStudy, IClimateAdaptContent)

    search_type = "ACTION"


class AdaptationOption(dexterity.Container):
    implements(IAdaptationOption, IClimateAdaptContent)

    search_type = "MEASURE"


@adapter(getSpecification(IAceMeasure['keywords']), IWidgetsLayer)
@implementer(IFieldWidget)
def KeywordsFieldWidget(field, request):
    widget = FieldWidget(field, AjaxSelectWidget(request))
    widget.vocabulary = 'eea.climateadapt.keywords'
    return widget


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
