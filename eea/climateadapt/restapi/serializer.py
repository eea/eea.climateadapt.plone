from eea.climateadapt.behaviors import IAdaptationOption, ICaseStudy
from eea.climateadapt.browser import get_date_updated, get_files
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from eea.climateadapt.interfaces import (IClimateAdaptContent,
                                         IEEAClimateAdaptInstalled)
# from plone.app.contenttypes.interfaces import IFolder
from plone.dexterity.interfaces import IDexterityContainer, IDexterityContent
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import (SerializeFolderToJson,
                                                SerializeToJson)
from zope.component import adapter
from zope.interface import Interface

# from plone import api


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

        result = append_common_new_fields(result, item)
        return result
