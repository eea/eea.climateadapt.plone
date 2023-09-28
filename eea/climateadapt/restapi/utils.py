import json

from eea.climateadapt.browser import get_date_updated, get_files
from eea.climateadapt.vocabulary import BIOREGIONS, ace_countries_dict
from plone.restapi.serializer.converters import json_compatible


def get_geographic(item, result={}):
    if not hasattr(item, 'geochars') and not item.geochars:
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


def cca_content_serializer(item, result):
    """ A generic enrichment that should be applied to all IClimateAdaptContent
    """

    result = get_geographic(item, result)

    files = get_files(item)
    if files:
        result["cca_files"] = [
            {"title": file.Title(), "url": file.absolute_url()} for file in files
        ]

    dates = get_date_updated(item)
    if not getattr(item, 'description', None) and hasattr(item, 'long_description') and item.long_description.output:
        description = item.portal_transforms.convertTo('text/plain',
                                                       item.long_description.output).getData().strip()
        result['description'] = description.decode('utf-8')

    result["cca_last_modified"] = json_compatible(
        dates["cadapt_last_modified"])
    result["cca_published"] = json_compatible(dates["cadapt_published"])
    result["is_cca_content"] = True
    result["language"] = getattr(item, "language", "en")

    return result
