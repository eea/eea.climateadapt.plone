from zope.interface import alsoProvides
from zope.schema import Date

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.autoform import directives
from z3c.form.interfaces import IAddForm, IEditForm
from plone.restapi.behaviors import BLOCKS_SCHEMA, LAYOUT_SCHEMA, IBlocks
from plone.schema import JSONField
from .volto_layout import guidance_layout_blocks, guidance_layout_items


class IGuidanceDocument(IAceItem, IBlocks):
    """Guidance Document Interface"""

    # directives.omitted(IEditForm, "featured")
    # directives.omitted(IAddForm, "featured")
    # directives.omitted(IEditForm, 'year')
    # directives.omitted(IAddForm, 'year')

    publication_date = Date(
        title=_("Date of item's publication"),
        description="The date refers to the latest date of publication"
        " of the item (different from the date of item's"
        " publication in Climate ADAPT)."
        " Please use the Calendar icon to add day/month/year. If you want to "
        'add only the year, please select "day: 1", "month: January" '
        "and then the year",
        required=True,
    )

    blocks = JSONField(
        title=_("Blocks"),
        description=_("The JSON representation of the object blocks."),
        schema=BLOCKS_SCHEMA,
        default=guidance_layout_blocks,
        required=False,
    )

    blocks_layout = JSONField(
        title=_("Blocks Layout"),
        description=_("The JSON representation of the object blocks layout."),
        schema=LAYOUT_SCHEMA,
        default={"items": guidance_layout_items},
        required=False,
    )


alsoProvides(IGuidanceDocument["publication_date"], ILanguageIndependentField)
