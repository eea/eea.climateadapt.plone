# override the defaults in https://github.com/plone/plone.restapi/blob/cdd2f72370f7f1f89d2a266ab80121d5da184880/src/plone/restapi/serializer/blocks.py#L273
# because they don't deal properly with urls with querystrings
import logging
import re

from urllib.parse import urlparse
from plone import api
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter


# from plone.base.utils import IBrowserRequest
# from plone.restapi.behaviors import IBlocks
# from plone.restapi.bbb import IPloneSiteRoot
# IBlockFieldSerializationTransformer,
# from eea.volto.policy.interfaces import IEeaVoltoPolicyLayer
# from zope.interface import implementer

logger = logging.getLogger("eea.climateadapt")


RESOLVE_UID_REGEXP = re.compile("resolveuid/([^/]+)")


def url_to_brain(url):
    """Find the catalog brain for a URL.

    Returns None if no item was found that is visible to the current user.
    """
    if not url:
        return
    if match := RESOLVE_UID_REGEXP.search(url):
        uid = match.group(1)
        query = {"UID": uid}
    else:
        # fallback in case the url wasn't converted to a UID
        try:
            parsed = urlparse(url)
            url = parsed.path
            if url.endswith("/"):
                url = url[:-1]
        except Exception:
            url = url
        path = "/".join(api.portal.get().getPhysicalPath()) + url
        query = {"path": {"query": path, "depth": 0}}
    catalog = api.portal.get_tool("portal_catalog")
    results = catalog.searchResults(**query)
    if results:
        return results[0]


def process_data(self, data, field=None):
    import pdb

    pdb.set_trace()
    value = data.get("href", "")
    if value:
        if "overwrite" not in data:
            # A block without this option is old and keeps the behavior
            # where data is not dynamically pulled from the href
            data["overwrite"] = True
            return data

        if isinstance(value, str):
            url = value
            value = [{"@id": url}]
        else:
            url = value[0].get("@id", "")

        if "?" in url:
            logger.info(
                f"Teaser url with querystring {self.context.absolute_url()} / {url}"
            )
        brain = url_to_brain(url)
        if brain is not None:
            serialized_brain = getMultiAdapter(
                (brain, self.request), ISerializeToJsonSummary
            )()

            if not data.get("overwrite"):
                # Update fields at the top level of the block data
                for key in ["title", "description", "head_title"]:
                    if key in serialized_brain:
                        data[key] = serialized_brain[key]

            # We return the serialized brain.
            value[0].update(serialized_brain)
            data["href"] = value
            if "?" in url:
                qs = urlparse(url).query
                data["href"][0]["@id"] = f"{data['href'][0]['@id']}?{qs}"
        elif not url.startswith("http"):
            # Source not found; emit a warning
            logger.info(
                "Teaser url path could not be translated to brain {value} / {self.context.absolute_url()"
            )
            data["href"] = [{"@id": url}]
    return data


# class TeaserBlockSerializerBase:
#     order = 0
#     block_type = "teaser"
#
#     def __init__(self, context, request):
#         self.context = context
#         self.request = request
#
#     def __call__(self, block):
#         return self._process_data(block)

# @implementer(IBlockFieldSerializationTransformer)
# @adapter(IBlocks, IBrowserRequest)
# class TeaserBlockSerializer(TeaserBlockSerializerBase):
#     """Serializer for content-types with IBlocks behavior"""
#
#
# @implementer(IBlockFieldSerializationTransformer)
# @adapter(IPloneSiteRoot, IBrowserRequest)
# class TeaserBlockSerializerRoot(TeaserBlockSerializerBase):
#     """Serializer for site root"""
