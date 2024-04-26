# pylint: disable=ungrouped-imports
"""
Indexer
"""

from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest

from eea.climateadapt.image_scales.interfaces import IImageScalesAdapter


@indexer(IDexterityContent)
def image_scales(obj):
    """
    Indexer used to store in metadata the image scales of the object.
    """
    # __import__("pdb").set_trace()
    adapter = queryMultiAdapter((obj, getRequest()), IImageScalesAdapter)
    if not adapter:
        # Raising an AttributeError does the right thing,
        # making sure nothing is saved in the catalog.
        raise AttributeError

    try:
        scales = adapter()
    except TypeError:
        scales = {}
    if not scales:
        raise AttributeError

    storage = PersistentDict(scales)
    # this is called twice:
    # - once triggered by the plone.app.multilingual reindex translations
    # - second time because it's detected as an object in the reindexing queue
    #   that needs to be reindexed
    # print("Calling once image_scales indexer %", obj, scales)
    # __import__("pdb").set_trace()
    return storage
