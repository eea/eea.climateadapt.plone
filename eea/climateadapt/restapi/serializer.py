import json

from eea.climateadapt.behaviors import (IAceItem, IAceMeasure, IAceProject,
                                        IAdaptationOption, ICaseStudy)
from eea.climateadapt.browser import get_date_updated, get_files
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from eea.climateadapt.interfaces import (IClimateAdaptContent,
                                         IEEAClimateAdaptInstalled)
from eea.climateadapt.vocabulary import BIOREGIONS, ace_countries_dict
from plone.dexterity.interfaces import IDexterityContainer, IDexterityContent
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.serializer.blocks import (SlateBlockSerializerBase,
                                             uid_to_url)
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import (SerializeFolderToJson,
                                                SerializeToJson)
from zope.component import adapter
from zope.interface import Interface, implementer


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


def append_common_new_fields(result, item):
    """Add here fields for any CCA content type"""
    result["cca_last_modified"] = json_compatible(
        get_date_updated(item)["cadapt_last_modified"]
    )
    result["cca_published"] = json_compatible(
        get_date_updated(item)["cadapt_published"]
    )
    result["is_cca_content"] = True
    result["language"] = getattr(item, "language", "")

    return result


@adapter(IDexterityContainer, IEEAClimateAdaptInstalled)
class LanguageGenericFolderSerializer(SerializeFolderToJson):
    def __call__(self, version=None, include_items=True):
        result = super(LanguageGenericFolderSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


@adapter(IDexterityContent, IEEAClimateAdaptInstalled)
class LanguageGenericSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(LanguageGenericSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["language"] = getattr(item, "language", "")

        return result


# @adapter(IFolder, Interface)
# class LanguageFolderSerializer(LanguageGenericSerializer):
#     """"""


@adapter(IAceItem, Interface)
class AceItemSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(AceItemSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context

        result = get_geographic(item, result)
        result = append_common_new_fields(result, item)
        return result


@adapter(IAceMeasure, Interface)
class AceMeasureSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(AceMeasureSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context

        result = get_geographic(item, result)
        result = append_common_new_fields(result, item)
        return result


@adapter(IClimateAdaptContent, Interface)
class ClimateAdaptContentSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(ClimateAdaptContentSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context

        files = get_files(item)
        result["cca_files"] = [
            {"title": file.Title(), "url": file.absolute_url()} for file in files
        ]
        result = append_common_new_fields(result, item)
        return result


@adapter(IAdaptationOption, Interface)
class AdaptationOptionSerializer(SerializeFolderToJson):        # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["related_case_studies"] = find_related_casestudies(item)
        result = get_geographic(item, result)
        result = append_common_new_fields(result, item)
        return result


@adapter(IAceProject, Interface)
class AceProjectSerializer(SerializeFolderToJson):        # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(AceProjectSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result = get_geographic(item, result)
        result = append_common_new_fields(result, item)
        return result


@adapter(ICaseStudy, Interface)
class CaseStudySerializer(SerializeFolderToJson):       # SerializeToJson
    def __call__(self, version=None, include_items=True):
        result = super(CaseStudySerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        images = item.contentValues({"portal_type": "Image"})
        suffix = "/@@images/image/large"
        result["cca_gallery"] = [
            {"title": image.Title(), "url": image.absolute_url() + suffix}
            for image in images
        ]

        files = get_files(item)
        result["cca_files"] = [
            {"title": file.Title(), "url": file.absolute_url()} for file in files
        ]

        result = get_geographic(item, result)
        result = append_common_new_fields(result, item)
        return result


def get_geographic(item, result={}):
    if not hasattr(item, 'geochars'):
        return result

    response = {}
    data = json.loads(item.geochars)
    if len(data['geoElements']['countries']):
        response['countries'] = [ace_countries_dict.get(x, x) for x in
                                 data['geoElements']['countries']]
    if data['geoElements']['macrotrans'] and len(data['geoElements'
                                                      ]['macrotrans']):
        response['transnational_region'] = [BIOREGIONS.get(x, x)
                                            for x in data['geoElements']['macrotrans']]

    if len(response):
        result['geographic'] = response
    return result
