# pylint: disable=ungrouped-imports
"""
Indexer
"""

from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
# from Acquisition import aq_inner
# from zope.schema import getFields

from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest
from eea.climateadapt.image_scales.interfaces import IImageScalesAdapter


@indexer(IDexterityContent)
def image_scales(obj):
    """
    Indexer used to store in metadata the image scales of the object.
    """
    # this next line can raise AttributeError, which is fine for indexing
    # __import__("pdb").set_trace()
    # annot = obj.__annotations__
    # plonescales = annot.get("plone.scale")
    #
    # if not plonescales:
    #     raise AttributeError
    #
    # obj = aq_inner(obj)
    # res = {}
    # for schema in iterSchemata(self.context):
    #     for name, field in getFields(schema).items():
    #         # serialize the field
    #         serializer = queryMultiAdapter(
    #             (field, obj, self.request), IImageScalesFieldAdapter
    #         )
    #         if serializer:
    #             scales = serializer()
    #             if scales:
    #                 res[name] = scales
    #     return res
    #
    # result = {}
    # scales = dict(plonescales)
    #
    # for scale in scales.values():
    #     ext = scale["mimetype"].split("/")[1]
    #     scale["download"] = "@@images/%s.%s" % (scale["uid"], ext)
    #     if "data" in scale:
    #         del scale["data"]

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

    return PersistentDict(scales)
