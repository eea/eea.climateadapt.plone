from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from plone.app.contenttypes.interfaces import IImage
from plone.app.textfield import RichText
from plone.autoform import directives
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.namedfile.field import NamedBlobImage
from z3c.form.interfaces import IAddForm, IEditForm
from z3c.relationfield.schema import RelationChoice, RelationList


class ICaseStudy(IAceMeasure):  # , IGeolocatable):
    """ Case study
    """

    directives.omitted(IEditForm, 'featured')
    directives.omitted(IAddForm, 'featured')
    directives.omitted(IEditForm, 'primephoto')
    directives.omitted(IAddForm, 'primephoto')
    directives.omitted(IEditForm, 'supphotos')
    directives.omitted(IAddForm, 'supphotos')

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'relatedItems')
    # directives.omitted(IAddForm, 'relatedItems')

    challenges = RichText(
        title=_(u"Challenges"), required=True, default=None,
        description=_(u"Describe what are the main climate change "
                      u"impacts/risks and related challenges addressed by the "
                      u"adaptation solutions proposed by the case study. "
                      u"Possibly include quantitate scenarios/projections of "
                      u"future climate change considered by the case study "
                      u"(5,000 characters limit):"),
    )

    objectives = RichText(
        title=_(u"Objectives"), required=True, default=None,
        description=_(u"Describe the objectives which triggered the "
                      u"adaptation measures (5,000 characters limit):"),
    )

    solutions = RichText(
        title=_(u"Solutions"), required=True, default=None,
        description=_(u"Describe the climate change adaptation solution(s) "
                      u"implemented (5,000 characters limit):"),
    )

    form.widget(relevance="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    relevance = List(
        title=_(u"Relevance"),
        required=True,
        missing_value=[],
        default=None,
        description=_(u"Select only one category below that best describes "
                      u"how relevant this case study is to climate change "
                      u"adaptation:"),
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_relevance",),
    )

    contact = RichText(
        title=_(u"Contact"), required=True, default=u"",
        description=_(u"Contact of reference (institution and persons) who is "
                      u"directly involved in the development and "
                      u"implementation of the case. (500 char limit) "))

    adaptationoptions = RelationList(
        title=u"Adaptation measures implemented in the case:",
        default=[],
        description=_(u"Select one or more adaptation options that this item "
                      u"relates to:"),
        value_type=RelationChoice(
            title=_(u"Related"),
            vocabulary="eea.climateadapt.adaptation_options"
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    primary_photo = NamedBlobImage(
        title=_(u"Primary photo"),
        required=False,
    )

    primary_photo_copyright = TextLine(
        title=_(u"Primary Photo Copyright"), required=False, default=u"",
        description=_(u"Copyright statement or other rights information for  "
                      u"the primary photo."))

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
