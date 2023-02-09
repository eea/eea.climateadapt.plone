from eea.climateadapt.behaviors import IAdaptationOption
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import Interface


@adapter(IAdaptationOption, Interface)
class AdaptationOptionSerializer(SerializeToJson):

    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
                version=None, include_items=True)
        item = self.context
        result['related_case_studies'] = find_related_casestudies(item)
        return result
