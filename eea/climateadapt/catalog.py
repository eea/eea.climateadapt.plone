from collective.cover.interfaces import ICover
from plone.indexer import indexer
from zope.annotation.interfaces import IAnnotations
from zope.interface import Interface
import json
from city_profile import ICityProfile


@indexer(Interface)
def imported_ids(object):
    annot = IAnnotations(object).get('eea.climateadapt.imported_ids')
    if annot is None:
        return
    return list(annot)


@indexer(Interface)
def aceitem_id(object):
    if hasattr(object, "_aceitem_id"):
        return object._aceitem_id


@indexer(Interface)
def acemeasure_id(object):
    if hasattr(object, "_acemeasure_id"):
        return object._acemeasure_id


@indexer(Interface)
def aceproject_id(object):
    if hasattr(object, "_aceproject_id"):
        return object._aceproject_id


@indexer(Interface)
def countries(object):
    """ Provides a list of countries this item "belongs" to

    We first look at the spatial_values attribute. If it doesn't exist, try to
    parse the geochars attribute
    """

    value = None

    if hasattr(object, 'spatial_values'):
        value = object.spatial_values

    if value:
        #print "Return spatial values", object, value
        return value

    if hasattr(object, 'geochars'):
        value = object.geochars
        if not value:
            return None

        value = json.loads(value)['geoElements'].get('countries', []) or None
        # if value:
        #     #print "Returning", object, value
        return value


@indexer(ICover)
def search_type(object):
    """
    """
    return "CONTENT"


@indexer(ICityProfile)
def city_sectors(city):
    return city.key_vulnerable_adaptation_sector


@indexer(ICityProfile)
def city_climate_impacts(city):
    return city.climate_impacts_risks_particularly_for_city_region


@indexer(ICityProfile)
def city_stage_implementation_cycle(city):
    return city.stage_of_the_implementation_cycle


@indexer(ICityProfile)
def city_countries(city):
    return [city.country]


@indexer(ICityProfile)
def city_long_description(city):
    return ""
