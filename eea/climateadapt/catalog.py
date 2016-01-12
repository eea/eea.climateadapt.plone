from plone.indexer import indexer
from zope.interface import Interface
import json


@indexer(Interface)
def imported_uuid(object):
    if hasattr(object, "_uuid"):
        return object._uuid


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
        print "Return spatial values", object, value
        return value

    if hasattr(object, 'geochars'):
        value = object.geochars
        if not value:
            return None

        value = json.loads(value)['geoElements'].get('countries', []) or None
        if value:
            print "Returning", object, value
        return value
