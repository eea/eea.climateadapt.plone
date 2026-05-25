# -*- coding: utf-8 -*-
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldLinkIntegrityRetriever
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.restapi.blocks_linkintegrity import get_urls_from_value


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class CCAObjectListLinksRetriever(object):
    """Retrieves links from object_list fields (items) used in CCA blocks.

    This covers blocks like ContentLinks, RelevantAceContent, and ASTNavigation
    where links are nested within an 'items' list.
    """

    order = 10
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        links = []
        # Typical CCA blocks store nested links in 'items'
        items = block.get("items", [])
        if not isinstance(items, list):
            items = []

        for item in items:
            if not isinstance(item, dict):
                continue

            # We check fields that are known to contain links in CCA object_lists
            for field in ["source", "href", "url"]:
                value = item.get(field)
                if not value:
                    continue

                for url in get_urls_from_value(value):
                    if url not in links:
                        links.append(url)

        # Also check some top-level fields that might be missing from
        # GenericBlockLinksRetriever (which covers url, href, preview_image)
        for field in ["linkTo", "image"]:
            value = block.get(field)
            if not value:
                continue
            for url in get_urls_from_value(value):
                if url not in links:
                    links.append(url)

        return links
