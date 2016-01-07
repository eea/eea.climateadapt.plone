from plone.indexer import indexer
from zope.interface import Interface


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
