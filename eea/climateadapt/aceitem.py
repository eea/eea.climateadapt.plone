from eea.climateadapt import MessageFactory as _
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implements
from zope.schema import Choice, TextLine, List, Bool, Int, Text


# from five import grok
# from zope import schema
# from zope.schema.interfaces import IContextSourceBinder
# from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
#
# from zope.interface import invariant, Invalid, implements
#
# from z3c.form import group, field
#
# from plone.namedfile.field import NamedImage, NamedFile
# from plone.namedfile.field import NamedBlobImage, NamedBlobFile
#
# from plone.app.textfield import RichText
#
# from z3c.relationfield.schema import RelationList, RelationChoice
# from plone.formwidget.contenttree import ObjPathSourceBinder


class IAceItem(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Item
    """

    title = TextLine(title=_(u"Title"), required=True)

    description = TextLine(title=(u"description"), required=True)

    data_type = Choice(title=_(u"Data Type"),
                       required=True,
                       vocabulary="eea.climateadapt.aceitems_datatypes")

    storage_type = Choice(title=_(u"Storage Type"),
                          required=True,
                          vocabulary="eea.climateadapt.aceitems_storagetypes")

    # TODO: "keyword" from SQL is Subject
    keywords = TextLine(title=_(u"Keywords"),
                        description=_(u"Keywords related to the project"),
                        required=False)

    spatial_layer = TextLine(title=_(u"Spatial Layer"),
                             required=False,
                             default=u""
                             )

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

    important = Bool(title=_(u"High importance"), required=False,
                     default=False)

    source = TextLine(title=_(u"Source"), required=True,)

    comments = TextLine(title=_(u"Comments"), required=False, default=u"")

    year = Int(title=_(u"Year"), required=True)

    geochars = Text(title=_(u"Geographic characterization"),
                    required=False, default=u"")

    # TODO: see if possible to use eea.promotions for this
    featured = List(title=_(u"Featured in location"),
                    description=_(u"TODO: Featured description here"),
                    required=False,
                    value_type=Choice(
                        vocabulary="eea.climateadapt.aceitems_featured",),
                    )

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

    pass


class IInformationPortal(IAceItem):

    pass


class IGuidanceDocument(IAceItem):

    pass


class ITool(IAceItem):

    pass


class IOrganization(IAceItem):

    pass


class PublicationReport(dexterity.Item):
    implements(IPublicationReport)


class InformationPortal(dexterity.Item):
    implements(IInformationPortal)


class GuidanceDocument(dexterity.Item):
    implements(IGuidanceDocument)


class Tool(dexterity.Item):
    implements(ITool)


class Organization(dexterity.Item):
    implements(IOrganization)
