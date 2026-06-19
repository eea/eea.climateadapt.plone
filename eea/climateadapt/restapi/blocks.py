import json
import re
import logging
from copy import deepcopy
from urllib.parse import urlparse

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


_IMAGE_EXTENSIONS_RE = re.compile(
    r'\.(?:png|jpe?g|gif|webp|svg|tiff?|bmp|ico)(\?[^"]*)?$',
    re.IGNORECASE,
)

_URL_KEY_PATTERN = re.compile(
    r'(?P<field>"(?:url|href|@id)"\s*:\s*")'
    r'(?P<prefix>(?:https?://[^/"]+)?)/en/'
)


def _get_site_root(context):
    try:
        return context.portal_url.getPortalObject()
    except Exception:
        return None


def _get_context_host(context):
    try:
        return urlparse(context.portal_url()).hostname
    except Exception:
        return None


def _is_internal_url(context, url):
    parsed = urlparse(url)

    if not parsed.scheme and not parsed.netloc:
        return parsed.path.startswith("/en/")

    if parsed.scheme not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    context_host = _get_context_host(context)

    hostname = hostname.lower()
    return (
        hostname
        in (
            "demo-climate-adapt.02pre.eea.europa.eu",
            "climate-adapt.eea.europa.eu",
        )
        or (context_host and hostname == context_host.lower())
    ) and parsed.path.startswith("/en/")


def _site_path_exists(context, path):
    site = _get_site_root(context)
    if site is None:
        return False

    path = path.lstrip("/")
    if not path:
        return False

    try:
        return site.unrestrictedTraverse(path, None) is not None
    except Exception:
        return False


def _has_translated_site_path(context, url, language):
    """Return True when url points to an existing target-language site path."""
    if not _is_internal_url(context, url):
        return False

    path = urlparse(url).path
    translated_path = path.replace("/en/", "/%s/" % language, 1)
    return _site_path_exists(context, translated_path)


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class TranslatedLanguageLinkFixer(object):
    """Generic block serialization transformer that rewrites internal
    ``/en/`` URL prefixes to ``/{language}/`` so that links in translated
    pages work correctly when opened in a new browser tab.
    """

    order = 200
    block_type = None  # applies to every block type

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        if not block:
            return block

        lang = getattr(self.context, "language", "en")
        if not lang or lang == "en":
            return block

        if block.get("@type") == "image":
            return block

        block_json = json.dumps(json_compatible(block))

        def _replace(m):
            """Replace /en/ only when the remainder of the URL value is not
            an image file path."""
            pos = m.end()
            close = block_json.find('"', pos)
            url_tail = block_json[pos:close] if close >= 0 else block_json[pos:]
            if _IMAGE_EXTENSIONS_RE.search(url_tail):
                return m.group(0)  # leave image URLs unchanged

            url = "{}{}".format(m.group("prefix"), "/en/" + url_tail)
            if not _has_translated_site_path(self.context, url, lang):
                return m.group(0)

            return f"{m.group('field')}{m.group('prefix')}/{lang}/"

        block_json = _URL_KEY_PATTERN.sub(_replace, block_json)
        return json.loads(block_json)


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
