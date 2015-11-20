from eea.climateadapt import MessageFactory as _
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implements
from zope.schema import Choice, TextLine, List, Bool, Int, Text, URI, Decimal


class IAceMeasure(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Measure
    """

    # company - this is always liferay in the data
    # group - same value for all

    # title - Provided by behaviour. Imported value comes from name column
    title = TextLine(title=_(u"Title"), required=True)

    # description - Provided by behaviour. Imported value comes from description column
    description = TextLine(title=_(u"description"), required=True)

    implementation_type = Choice(
        title=_(u"Implementation Type"), required=False, default=None,
        vocabulary="eea.climateadapt.acemeasure_implementationtype"
    )

    implementation_time = TextLine(
        title=_(u"Implementation Time"), required=False, default=None,
    )

    lifetime = TextLine(title=_(u"Lifetime"), required=False, default=u"")

    spatial_layer = TextLine(
        title=_(u"Spatial Layer"), required=False, default=u"")

    spatial_values = List(
        title=_(u"Countries"), required=False, default=None,
        value_type=Choice(vocabulary="eea.climateadapt.ace_countries"),
    )

    legal_aspects = Text(title=_(u"Legal aspects"),
                         required=False,
                         default=u"")

    stakeholder_participation = Text(
        title=_(u"Stakeholder participation"), required=False,
        default=u"")

    contact = RichText(title=_(u"Contact"), required=False, default=u"")

    success_limitations = Text(
        title=_(u"Success / limitations"), required=False, default=u"")

    cost_benefit = Text(
        title=_(u"Cost / Benefit"), required=False, default=u"")

    websites = List(title=_(u"Websites"),
                    description=_(u"A list of relevant website links"),
                    required=False,
                    value_type=URI(title=_("A link")),
                    )

    # TODO: "keywords" from SQL is Subject
    keywords = TextLine(title=_(u"Keywords"),
                        description=_(u"Keywords related to the project"),
                        required=False)

    # TODO: startdate, enddate, publicationdate have no values in DB
    # TODO: specialtagging is not used in any view jsp, only in add and edit
    # views

    sectors = List(title=_(u"Sectors"),
                   description=_(u"TODO: Sectors description here"),
                   required=False,
                   value_type=Choice(
                       vocabulary="eea.climateadapt.aceitems_sectors",),
                   )

    elements = List(title=_(u"Elements"),
                    description=_(u"TODO: Elements description here"),
                    required=False,
                    value_type=Choice(
                        vocabulary="eea.climateadapt.aceitems_elements",),
                    )

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"TODO: Climate impacts description here"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",),
    )

    source = TextLine(title=_(u"Source"), required=True,)
    # TODO: special tagging implement as related

    geochars = Text(title=_(u"Geographic characterization"),
                    required=False, default=u"")

    measure_type = Choice(title=_(u"Measure Type"),
                          required=True,
                          default="A",
                          vocabulary="eea.climateadapt.acemeasure_types")

    comments = TextLine(title=_(u"Comments"), required=False, default=u"")

    important = Bool(title=_(u"High importance"), required=False,
                     default=False)

    rating = Int(title=_(u"Rating"), required=True, default=0)

    # approved is done by workflow


class ICaseStudy(IAceMeasure):
    """ Case study
    """
    # location - a clickable map, not provided if is "Adaptation option" type

    location_lat = Decimal(title=_(u"Location latitude"), required=True)
    location_lon = Decimal(title=_(u"Location longitude"), required=True)


class IAdaptationOption(IAceMeasure):
    """ Adaptation Option
    """


class CaseStudy(dexterity.Item):
    implements(ICaseStudy)

    search_type = "ACTION"


class AdaptationOption(dexterity.Item):
    implements(IAdaptationOption)

    search_type = "MEASUREACTION"


# class AceMeasure(Base):
#     __tablename__ = 'ace_measure'
#
#     measureid = Column(BigInteger, primary_key=True, server_default=text("nextval('ace_measure_id_seq'::regclass)"))
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
#     specialtagging = Column(String(75), server_default=text("NULL::character varying"))
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
