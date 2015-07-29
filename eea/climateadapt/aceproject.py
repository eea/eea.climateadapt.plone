from eea.climateadapt import MessageFactory as _
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope.interface import implements
from zope.schema import Choice, TextLine, List, Bool, Text


class IAceProject(form.Schema, IImageScaleTraversable):
    """
    Defines content-type schema for Ace Project
    """

    title = TextLine(title=_(u"Title"),
                     description=_(u"Project title or name"),
                     required=True,
                     )

    acronym = TextLine(title=_(u"Acronym"),
                       description=_(u"Acronym of the project"),
                       required=True,
                       )

    lead = TextLine(title=_(u"Lead"),
                    description=_(u"Lead organisation of the project"),
                    required=False,
                    )

    website = TextLine(title=_(u"Website"),
                       description=_(u"Project website"),
                       required=False,
                       )

    abstracts = TextLine(title=_(u"Abstracts"),
                         description=_(u"Project abstracts"),
                         required=False,
                         )

    partners = TextLine(title=_(u"Parners"),
                        description=_(u"Information about project partners"),
                        required=False,
                        )

    keywords = TextLine(title=_(u"Keywords"),
                        description=_(u"Keywords related to the project"),
                        required=False,
                        )

    sectors = List(title=_(u"Sectors"),
                   description=_(u"EU policy sectors"),
                   required=False,
                   value_type=Choice(
                       vocabulary="eea.climateadapt.aceitems_sectors",),
                   )

    elements = List(title=_(u"Elements"),
                    description=_(u"Adaptation element"),
                    required=False,
                    value_type=Choice(
                        vocabulary="eea.climateadapt.aceitems_elements",),
                    )

    climate_impacts = List(
        title=_(u"Climate impacts"),
        description=_(u"Climate impacts"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_climateimpacts",),
    )

    funding = TextLine(title=_(u"Funding"),
                       description=_(u"Source of funding"),
                       required=False,
                       )

    duration = TextLine(title=_(u"Duration"),
                        description=_(u"Duration of project"),
                        required=False,
                        )

    source = TextLine(
        title=_(u"Source"),
        description=_(u"Source from which project was retrieved"),
        required=False)

    specialtagging = TextLine(
        title=_(u"Special Tagging"),
        description=_(u"Special tags that allow for linking the item"),
        required=False)

    geochars = Text(title=_(u"Geochars"),
                    description=_(u"Characterisation of the area"),
                    required=False)

    countries = List(title=_(u"Countries"),
                     description=_(u"European countries"),
                     required=False,
                     value_type=Choice(
                         vocabulary="eea.climateadapt.ace_countries"))

    comments = TextLine(title=_(u"Source"),
                        description=_(u"Any comments provided with the item"),
                        required=False)

    important = Bool(title=_(u"Important"),
                     required=False,
                     default=False)


class AceProject(dexterity.Item):
    implements(IAceProject)
