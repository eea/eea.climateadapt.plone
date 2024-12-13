# NOTE: this is not actually used and loaded

import logging
import json
from collections import deque

from plone.restapi.interfaces import IExpandableElement
from zope.component import adapter
from zope.interface import Interface, implementer

from eea.climateadapt.interfaces import ITransnationalRegionMarker
# from eea.climateadapt.tiles.transregional_select import get_countries, get_regions
# from eea.climateadapt.translation.utils import get_current_language

logger = logging.getLogger("eea.climateadapt")


def iterate_tiles(cover_layout):
    queue = deque(cover_layout)

    while queue:
        child = queue.pop()
        if child.get("tile-type"):
            yield child
        if "children" in child:
            queue.extend(child["children"])


@implementer(IExpandableElement)
@adapter(ITransnationalRegionMarker, Interface)
class TransnationalRegion(object):
    """An expander that automatically inserts the information about the
    countries belonging to a transnational region"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        try:
            # current_lang = get_current_language(self.context, self.request)
            current_lang = "en"

            if "index_html" in self.context.contentIds():
                cover = self.context["index_html"]
            else:
                cover = self.context

            tile_id = None

            layout = json.loads(cover.cover_layout)
            for tile in iterate_tiles(layout):
                if tile.get("tile-type") == "eea.climateadapt.transregionselect":
                    tile_id = tile["id"]

            if not tile_id:
                return {}

            # TODO: this needs to be reimplemented as a behavior when we move to Plone 6 and get rid of Covers

            tile_data = cover.get_tile(tile_id).data
        except Exception as e:
            logger.warning("Error in processing transnational region: {}".format(e))
            tile_data = {}

        result = {
            "transnationalregion": {
                "@id": "{}/@transnationalregion".format(self.context.absolute_url()),
                # TODO plone6 this needs to be migrated
                # "regions": get_regions(current_lang),
                # "countries": get_countries(self.context, tile_data, current_lang),
            }
        }

        print(result)

        return result
