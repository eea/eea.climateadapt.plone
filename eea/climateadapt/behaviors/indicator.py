from zope.schema import (URI, Bool, Choice, Date, Datetime, Int, List, Text,
                         TextLine, Tuple)

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm


class IIndicator(IAceItem):
    """ Indicator Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    map_graphs = Text(title=_(u"Map/Graphs"), required=False)

    publication_date = Date(
        title=_(u"Date of item's publication"),
        description=u"The date refers to the latest date of publication of "
        u"the item."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u"add only the year, please select \"day: 1\", \"month: January\" "
        u"and then the year",
        required=True,
    )
