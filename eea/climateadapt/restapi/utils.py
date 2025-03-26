import json

from plone.dexterity.utils import iterSchemata
from plone.restapi.serializer.converters import json_compatible
from zope.schema import getFields

from eea.climateadapt.browser import get_date_updated, get_files
from eea.climateadapt.vocabulary import BIOREGIONS, ace_countries_dict


def get_geographic(item, result={}):
    if not hasattr(item, "geochars") and not item.geochars:
        return result

    response = {}
    if item.geochars is not None and item.geochars != "":
        data = json.loads(item.geochars)
    else:
        data = {}

    if not data:
        return result

    if "countries" in data["geoElements"] and len(data["geoElements"]["countries"]):
        response["countries"] = [
            ace_countries_dict.get(x, x) for x in data["geoElements"]["countries"]
        ]
    if (
        "macrotrans" in data["geoElements"]
        and data["geoElements"]["macrotrans"]
        and len(data["geoElements"]["macrotrans"])
    ):
        response["transnational_region"] = [
            BIOREGIONS.get(x, x) for x in data["geoElements"]["macrotrans"]
        ]

    if len(response):
        result["geographic"] = response

    return result


def use_blocks_from_fti(context, result):
    blocks = None
    blocks_layout = None

    for schema in iterSchemata(context):
        for name, field in getFields(schema).items():
            if name == "blocks" and field.default and not blocks:
                blocks = field.default
            if name == "blocks_layout" and field.default and not blocks_layout:
                blocks_layout = field.default
    if blocks:
        result["blocks"] = blocks
        result["blocks_layout"] = blocks_layout

    return result


def cca_content_serializer(item, result, request):
    """A generic enrichment that should be applied to all IClimateAdaptContent"""

    result = get_geographic(item, result)

    files = get_files(item)
    if files:
        result["cca_files"] = [
            {"title": file.Title(), "url": file.absolute_url()} for file in files
        ]

    dates = get_date_updated(item)

    if (
        hasattr(item, "long_description")
        and item.long_description
        and item.long_description.output
        and "eea_index" in request.form
    ):
        converted = item.portal_transforms.convertTo(
            "text/plain", item.long_description.output
        )
        if converted is not None:
            description = converted.getData().strip()
            try:
                if isinstance(description, str):
                    result["description"] = description
                else:
                    result["description"] = description.decode("utf-8")
            except Exception:
                result["description"] = description.encode("utf-8")
        else:
            result["description"] = ""

    result["cca_last_modified"] = json_compatible(
        dates["cadapt_last_modified"])
    result["cca_published"] = json_compatible(dates["cadapt_published"])
    result["is_cca_content"] = True
    result["language"] = getattr(item, "language", "en")

    result = use_blocks_from_fti(item, result)

    return result
