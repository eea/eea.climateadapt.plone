from eea.climateadapt.behaviors import (IAceProject, IAdaptationOption,
                                        ICaseStudy)
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from eea.climateadapt.interfaces import (IClimateAdaptContent,
                                         IEEAClimateAdaptInstalled)
from plone.dexterity.interfaces import IDexterityContainer, IDexterityContent
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import (SlateBlockSerializerBase,
                                             uid_to_url)
from plone.restapi.serializer.dxcontent import (SerializeFolderToJson,
                                                SerializeToJson)
from zope.component import adapter
from zope.interface import Interface, implementer

from .utils import cca_content_serializer


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IEEAClimateAdaptInstalled)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    # TODO: this needs also a deserializer that takes the scale in url and saves it to
    # the "scale" field

    def handle_img(self, child):
        if child.get("url"):
            url = uid_to_url(child["url"])
            if child.get('scale'):
                url = "%s/@@images/image/%s" % (url, child['scale'])
            else:
                url = "%s/@@images/image/large" % url

            child["url"] = url


@adapter(IDexterityContainer, IEEAClimateAdaptInstalled)
class GenericFolderSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(GenericFolderSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IDexterityContent, IEEAClimateAdaptInstalled)
class GenericContentSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(GenericContentSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IClimateAdaptContent, Interface)
class ClimateAdaptContentSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(ClimateAdaptContentSerializer, self).__call__(
            version=None, include_items=True
        )
        return cca_content_serializer(self.context, result, self.request)


@adapter(IAdaptationOption, Interface)
# SerializeToJson
class AdaptationOptionSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
            version=None, include_items=True
        )
        result["related_case_studies"] = find_related_casestudies(self.context)
        return cca_content_serializer(self.context, result, self.request)


@adapter(IAceProject, Interface)
class AceProjectSerializer(SerializeFolderToJson):        # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(AceProjectSerializer, self).__call__(
            version=None, include_items=True
        )
        return cca_content_serializer(self.context, result, self.request)


@adapter(ICaseStudy, Interface)
class CaseStudySerializer(SerializeFolderToJson):       # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(CaseStudySerializer, self).__call__(
            version=None, include_items=True
        )
        result = cca_content_serializer(self.context, result, self.request)

        item = self.context
        images = item.contentValues({"portal_type": "Image"})
        suffix = "/@@images/image/large"
        result["cca_gallery"] = [
            {"title": image.Title(), "url": image.absolute_url() + suffix}
            for image in images
        ]

        return result
