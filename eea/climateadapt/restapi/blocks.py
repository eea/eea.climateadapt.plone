import json
import logging
from copy import deepcopy

from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import (
    IBlockFieldDeserializationTransformer,
    IBlockFieldSerializationTransformer,
)
from plone.restapi.serializer.blocks import uid_to_url
from plone.restapi.serializer.converters import json_compatible
from six import string_types
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from eea.climateadapt.tiles.search_acecontent import AceTileMixin

logger = logging.getLogger("eea.climateadapt")


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class GenericLinkFixer(object):
    order = -2
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if block:
            converted = json_compatible(block)
            dumped = json.dumps(converted)
            if "next-climate-adapt.eea.europa" in dumped:
                dumped = dumped.replace("next-climate-adapt", "climate-adapt")
                block = json.loads(dumped)

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SearchAceContentBlockSerializer(object):
    order = 100
    block_type = "searchAceContent"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        ace = AceTileMixin()
        ace.context = self.context
        ace.request = self.request
        ace.data = deepcopy(block)
        ace.current_lang = "en"

        block["_v_results"] = ace.sections()

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ColumnBlockSerializationTransformer(object):
    order = 100
    block_type = "columnsBlock"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        data = block.get("data", {})
        blocks_layout = data.get("blocks_layout", {}).get("items", [])
        blocks = data.get("blocks", {})
        for uid in list(blocks.keys()):
            if uid not in blocks_layout:
                logger.warn("Removing unreferenced block in columnsBlock: %s", uid)
                del blocks[uid]

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class RastBlockSerializationTransformer(object):
    order = 100
    block_type = "rastBlock"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if block.get("root_path"):
            block["root_path"] = block["root_path"].replace(
                "/en/", "/%s/" % (self.context.language or "en")
            )

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ListingBlockSerializationTransformer(object):
    order = 100
    block_type = "listing"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        query = block.get("querystring", {}).get("query", [])
        defaultLang = getattr(self.context, "language", "en")

        for filt in query:
            if filt.get("i") == "path":
                path = filt.get("v", "")
                if path.startswith("/en/"):
                    filt["v"] = path.replace("/en/", "/%s/" % defaultLang)

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class RelevantAceContentBlockSerializer(object):
    order = 100
    block_type = "rastBlock"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if block.get("root_path"):
            block["root_path"] = block["root_path"].replace(
                "/en/", "/%s/" % (self.context.language or "en")
            )

        return block


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SearchlibBlockSerializationTransformer(object):
    order = 100
    block_type = "searchlib"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        defaultFilters = block.get("defaultFilters", [])
        defaultLang = getattr(self.context, "language", "en")

        for filt in defaultFilters:
            if filt.get("name") == "language":
                filt["value"] = {
                    "field": "language",
                    "type": "any",
                    "values": [defaultLang],
                }

        return block


# @implementer(IBlockFieldSerializationTransformer)
# @adapter(IBlocks, IBrowserRequest)
# class RelevantAceContentBlockSerializer(object):
#     order = 100
#     block_type = "relevantAceContent"

#     def __init__(self, context, request):
#         self.context = context
#         self.request = request

#     def __call__(self, block):
#         ace = AceTileMixin()
#         ace.context = self.context
#         ace.request = self.request
#         ace.data = block
#         ace.current_lang = "en"

#         if not block.get("items"):
#             block["_v_results"] = ace.relevant_all_items()

#         return block


class ResolveUIDDeserializerBase(object):
    """The "url" smart block field.

    This is a generic handler. In all blocks, it converts any "url"
    field from using resolveuid to an "absolute" URL

    This is a copy of the one in restapi, to handle the "image" field
    """

    order = 10
    block_type = None
    disabled = False
    fields = ["image"]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        for field in self.fields:
            link = block.get(field, "")
            if link and isinstance(link, string_types):
                block[field] = path2uid(context=self.context, link=link)
            elif link and isinstance(link, list):
                # Detect if it has an object inside with an "@id" key (object_widget)
                if len(link) > 0 and isinstance(link[0], dict) and "@id" in link[0]:
                    result = []
                    for item in link:
                        item_clone = deepcopy(item)
                        item_clone["@id"] = path2uid(
                            context=self.context, link=item_clone["@id"]
                        )
                        result.append(item_clone)

                    block[field] = result
                elif len(link) > 0 and isinstance(link[0], string_types):
                    block[field] = [
                        path2uid(context=self.context, link=item) for item in link
                    ]
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ResolveUIDDeserializer(ResolveUIDDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


class ResolveUIDSerializerBase(object):
    order = 1
    block_type = None
    disabled = False
    fields = ["image"]  # provide support for tabsBlock image assets

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        for field in self.fields:
            if field in list(value.keys()):
                link = value.get(field, "")
                if isinstance(link, string_types):
                    value[field] = uid_to_url(link)
                elif isinstance(link, list):
                    if len(link) > 0 and isinstance(link[0], dict) and "@id" in link[0]:
                        result = []
                        for item in link:
                            item_clone = deepcopy(item)
                            item_clone["@id"] = uid_to_url(item_clone["@id"])
                            result.append(item_clone)

                        value[field] = result
                    elif len(link) > 0 and isinstance(link[0], string_types):
                        value[field] = [uid_to_url(item) for item in link]
        return value


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ResolveUIDSerializer(ResolveUIDSerializerBase):
    """Serializer for content-types with IBlocks behavior"""
