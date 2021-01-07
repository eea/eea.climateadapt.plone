from zope.schema import Date

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm


class IGuidanceDocument(IAceItem):
    """Guidance Document Interface"""

    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")
    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')

    publication_date = Date(
        title=_(u"Date of item's publication"),
        description=u"The date refers to the latest date of publication"
        u" of the item (different from the date of item's"
        u" publication in Climate ADAPT)",
        required=False,
    )
