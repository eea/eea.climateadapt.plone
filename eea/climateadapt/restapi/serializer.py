from zope.component import adapter
from eea.climateadapt.behaviors import IAdaptationOption
from zope.interface import Interface
from plone.restapi.serializer.dxcontent import SerializeToJson
from eea.climateadapt.browser.adaptationoption import find_related_casestudies


@adapter(IAdaptationOption, Interface)
class AdaptationOptionSerializer(SerializeToJson):

    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
                version=None, include_items=True)
        result["zzztestvalue"] = "TEST VALUE"
        item = self.context
        # __import__('pdb').set_trace()
        # related_case_studies = find_related_casestudies(item)
        return result
