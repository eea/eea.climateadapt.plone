""" Utilities to convert to streamlined HTML and from HTML to volto blocks

The intention is to use eTranslation as a service to translate a complete Volto page with blocks
by first converting the blocks to HTML, then ingest and convert that structure back to Volto blocks
"""


from Products.Five.browser import BrowserView


class VoltoBlocksToHtml(BrowserView):
    pass
