from eea.climateadapt.interfaces import IEEAClimateAdaptInstalled
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter


@adapter(IDexterityContent, IEEAClimateAdaptInstalled)
class LanguageSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(LanguageSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")
        
        return result
