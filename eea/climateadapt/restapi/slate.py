from collections import deque

from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import transform_links
from plone.restapi.interfaces import IBlockFieldSerializationTransformer

from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.serializer.blocks import uid_to_url

# from plone.restapi.bbb import IPloneSiteRoot
# from plone.restapi.serializer.utils import uid_to_url
# from plone.restapi.blocks import visit_blocks, iter_block_transform_handlers
# from plone.restapi.interfaces import IFieldSerializer
# from plone.restapi.serializer.converters import json_compatible
# from plone.restapi.serializer.dxfields import DefaultFieldSerializer
# from plone.restapi.serializer.utils import resolve_uid, uid_to_url
# from plone.restapi.deserializer.blocks import iterate_children
# from plone.restapi.deserializer.blocks import SlateBlockTransformer


def iterate_children(value):
    """iterate_children.

    :param value:
    """
    queue = deque(value)
    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])


class SlateBlockTransformer:
    """SlateBlockTransformer."""

    field = "value"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        value = (block or {}).get(self.field, [])
        children = iterate_children(value or [])

        for child in children:
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, "handle_%s" % node_type, None)
                if handler:
                    handler(child)

        return block


class SlateBlockSerializerBase(SlateBlockTransformer):
    """SlateBlockSerializerBase."""

    order = 100
    block_type = "slate"
    disabled = False

    def _uid_to_url(self, context, path):
        return uid_to_url(path)

    def handle_a(self, child):
        transform_links(self.context, child, transformer=self._uid_to_url)

    def handle_link(self, child):
        if child.get("data", {}).get("url"):
            child["data"]["url"] = uid_to_url(child["data"]["url"])

    def handle_img(self, child):
        if child.get("url"):
            child["url"] = uid_to_url(child["url"]) + "/@@images/image/mini"


class SlateTableBlockSerializerBase(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    order = 100
    block_type = "slateTable"

    def __call__(self, block):
        """call"""
        # __import__("pdb").set_trace()
        rows = block.get("table", {}).get("rows", [])
        for row in rows:
            cells = row.get("cells", [])

            for cell in cells:
                cellvalue = cell.get("value", [])
                children = iterate_children(cellvalue or [])
                for child in children:
                    node_type = child.get("type")
                    if node_type:
                        handler = getattr(self, "handle_%s" % node_type, None)
                        if handler:
                            handler(child)

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateTableBlockSerializer(SlateTableBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


# @implementer(IBlockFieldSerializationTransformer)
# @adapter(IPloneSiteRoot, IBrowserRequest)
# class SlateTableBlockSerializerRoot(SlateTableBlockSerializerBase):
#     """Serializer for site root"""
