# NOTE: this is not actually used and loaded

from plone.api import content
from plone.restapi.interfaces import IExpandableElement, ISerializeToJsonSummary
from zope.component import adapter, getMultiAdapter
from zope.interface import Interface, implementer

from eea.climateadapt.interfaces import ITransnationalRegionMarker


@implementer(IExpandableElement)
@adapter(ITransnationalRegionMarker, Interface)
class TransnationalRegion(object):
    """An expander that automatically inserts the information about the
    countries belonging to a transnational region"""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        brains = content.find(
            context=self.context,
            depth=1,
            object_provides=["eea.climateadapt.interfaces.ITransnationalRegionMarker"],
            review_state="published",
        )
        result = {
            "transnationalregion": {
                "@id": "{}/@transnationalregion".format(self.context.absolute_url()),
                "countries": [
                    getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
                    for brain in brains
                ],
            }
        }

        # catalog = portal.get_tool('portal_catalog')

        return result
