from zope.interface import alsoProvides
from zope.schema import TextLine

from eea.climateadapt import CcaAdminMessageFactory as _
from eea.climateadapt.behaviors.aceitem import IAceItem
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField

class IMapGraphDataset(IAceItem):
    """Maps, Graphs and Datasets Interface"""

    gis_layer_id = TextLine(
        title=_(u"GIS Layer ID"),
        description=u"Enter the layer id for the map-viewer " u"(250 character limit)",
        required=False,
        default=u"",
    )


alsoProvides(IMapGraphDataset["gis_layer_id"], ILanguageIndependentField)
