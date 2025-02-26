from zope.component import getMultiAdapter
from plone.restapi.interfaces import ISerializeToJson
from zope.interface import Interface


class ITranslationValue(Interface):
    """Adapters for translation values"""


class MissionFundingDescriptionValue(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        serializer = getMultiAdapter(
            (self.context, self.request), ISerializeToJson)
        serialized = serializer(version=None, include_items=False)
        return serialized["description"]
