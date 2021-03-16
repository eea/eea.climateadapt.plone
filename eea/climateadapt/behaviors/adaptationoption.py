from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from plone.autoform import directives
from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm
from z3c.relationfield.schema import RelationChoice, RelationList


class IAdaptationOption(IAceMeasure):
    """ Adaptation Option
    """

    directives.omitted(IEditForm, 'featured')
    directives.omitted(IAddForm, 'featured')

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')

    form.widget(category="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    category = List(
        title=_(u"General category"),
        description=_(u"Select one or more categories of adaptation options. "
                      u"The 3 options are:"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_category",),
    )

    form.widget(ipcc_category="z3c.form.browser.checkbox.CheckBoxFieldWidget")
    ipcc_category = List(
        title=_(u"IPCC adaptation options categories"),
        description=_(u"Select one or more categories of adaptation options. "
                      u"The options are:"),
        required=False,
        value_type=Choice(
            vocabulary="eea.climateadapt.aceitems_ipcc_category",),
    )

    casestudies = RelationList(
        title=u"Case studies implemented in the adaption",
        default=[],
        description=_(u"Select one or more case study that this item "
                      u"relates to:"),
        value_type=RelationChoice(
            title=_(u"Related"),
            vocabulary="eea.climateadapt.case_studies"
            # source=ObjPathSourceBinder(),
            # source=CatalogSource(portal_type='eea.climateadapt.adaptionoption'),
        ),
        required=False,
    )

    publication_date = Date(
        title=_(u"Date of item's creation"),
        description=u"The date refers to the moment in which the item "
        u"has been prepared or  updated by contributing "
        u"experts to be submitted for the publication in "
        u"Climate ADAPT."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u"add only the year, please select \"day: 1\", \"month: January\" "
        u"and then the year",
        required=True
    )
