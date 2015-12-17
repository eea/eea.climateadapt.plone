from plone.indexer import indexer
from zope.interface import Interface


@indexer(Interface)
def imported_uuid(object):
    if hasattr(object, "_uuid"):
        return object._uuid
