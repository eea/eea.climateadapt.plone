from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform import directives
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from z3c.form.interfaces import IAddForm, IEditForm
from zope.interface import alsoProvides
from zope.schema import Date, Text, TextLine

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem

from .volto_layout import indicator_layout_blocks, indicator_layout_items


class IIndicator(IAceItem, IBlocks):
    """Indicator Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")

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
        title=_("Date of item's publication"),
        description="The date refers to the latest date of publication of "
        "the item."
        " Please use the Calendar icon to add day/month/year. If you want to "
        'add only the year, please select "day: 1", "month: January" '
        "and then the year",
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
        default={"items": indicator_layout_items},
        required=False,
    )


alsoProvides(IIndicator["publication_date"], ILanguageIndependentField)
