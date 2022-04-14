# from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm


class ITool(IAceItem):
    """Tool Interface"""

    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    # source = TextLine(title=_(u"Organisation's source"),
    #                  required=False,
    #                  description=u"Describe the original source of the item "
    #                              u"description (250 character limit)")
