from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class VolatileSmartField(object):
    """When deserializing block values, delete all block fields that start with `_v_`"""

    order = float("inf")
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        keys = [k for k in block.keys() if k.startswith("_v_")]
        for k in keys:
            del block[k]

        return block
