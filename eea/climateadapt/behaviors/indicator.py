from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from zope.interface import alsoProvides
from zope.schema import Date, Text, TextLine, Bool

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem

from .volto_layout import indicator_layout_blocks, indicator_layout_items

# from plone.autoform import directives
# from z3c.form.interfaces import IAddForm, IEditForm


class IIndicator(IAceItem, IBlocks):
    """Indicator Interface"""

    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')
    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")

    map_graphs = Text(
        title=_("Map/Graphs"),
        required=False,
        description="Enter an iframe embed code, a Flourish embed code, "
        "or a direct URL (which will be embedded as an iframe) "
        "to display an interactive visualization.",
    )

    map_graphs_height = TextLine(
        title=_("Map/Graphs Height"),
        description="Height of the iframe (e.g., 750).",
        required=False,
    )

    map_graphs_full_width = Bool(
        title=_("Full-width map/graph"),
        description=_(
        "If enabled, the map/graph visualization will use the full container width. "
        "If disabled, it will remain in the left column."
        ),
        required=False,
        default=False,
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
