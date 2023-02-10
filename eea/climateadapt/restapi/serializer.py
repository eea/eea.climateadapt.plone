from eea.climateadapt.behaviors import IAdaptationOption

# from eea.climateadapt.behaviors.acemeasure import IAceMeasure
from eea.climateadapt.interfaces import IClimateAdaptContent
from eea.climateadapt.browser.adaptationoption import find_related_casestudies
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import Interface
from plone.restapi.serializer.converters import json_compatible


def get_date_updated(item):
    wh = item.workflow_history
    wf = wh.get("cca_items_workflow", None)

    response = {}
    response["cadapt_last_modified"] = item.modified()
    response["cadapt_published"] = item.effective()

    if not wf:
        return response

    for metadata in wf:
        if metadata["action"] == "publish":
            response["cadapt_published"] = metadata["time"]

    return response


def append_common_new_fields(result, item):
    """Add here fields for any CCA content type"""
    result["cca_last_modified"] = json_compatible(
        get_date_updated(item)["cadapt_last_modified"]
    )
    result["cca_published"] = json_compatible(
        get_date_updated(item)["cadapt_published"]
    )
    result["is_cca_content"] = True
    return result


@adapter(IClimateAdaptContent, Interface)
class ClimateAdaptContentSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(ClimateAdaptContentSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result = append_common_new_fields(result, item)
        return result


@adapter(IAdaptationOption, Interface)
class AdaptationOptionSerializer(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(AdaptationOptionSerializer, self).__call__(
            version=None, include_items=True
        )
        item = self.context
        result["related_case_studies"] = find_related_casestudies(item)
        result = append_common_new_fields(result, item)
        return result
