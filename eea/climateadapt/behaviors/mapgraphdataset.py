from zope.schema import TextLine

from eea.climateadapt import MessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem


class IMapGraphDataset(IAceItem):
    """Maps, Graphs and Datasets Interface"""

    gis_layer_id = TextLine(
        title=_(u"GIS Layer ID"),
        description=u"Enter the layer id for the map-viewer " u"(250 character limit)",
        required=False,
        default=u"",
    )
