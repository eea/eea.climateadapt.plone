from zope.interface import alsoProvides
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from zope.schema import Date, Text, TextLine
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from .volto_layout import indicator_layout_blocks, indicator_layout_items


class IIndicator(IAceItem, IBlocks):
    """ Indicator Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    directives.omitted(IEditForm, "featured")
    directives.omitted(IAddForm, "featured")

    map_graphs = Text(
        title=_(u"Map/Graphs"),
        required=False,
        description=u"Enter an iframe embed code, a Flourish embed code, "
                    u"or a direct URL (which will be embedded as an iframe) "
                    u"to display an interactive visualization.",
    )
    
    map_graphs_height = TextLine(
        title=_(u"Map/Graphs Height"),
        description=u"Height of the iframe (e.g., 750).",
        required=False,
    )

    publication_date = Date(
        title=_(u"Date of item's publication"),
        description=u"The date refers to the latest date of publication of "
        u"the item."
        u" Please use the Calendar icon to add day/month/year. If you want to "
        u"add only the year, please select \"day: 1\", \"month: January\" "
        u"and then the year",
        required=True,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=indicator_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={
            "items": indicator_layout_items
        },
        required=False,
    )

alsoProvides(IIndicator['publication_date'], ILanguageIndependentField)
