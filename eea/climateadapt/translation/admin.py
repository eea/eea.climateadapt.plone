"""Admin translation"""

# import json
import logging
from collections import defaultdict

from eea.climateadapt.blocks import BlocksTraverser, BlockType
from Products.Five.browser import BrowserView
from zope.site.hooks import getSite

logger = logging.getLogger("eea.climateadapt")


def is_obj_skipped_for_translation(obj):
    # skip by portal types
    if obj.portal_type in ["eea.climateadapt.city_profile", "LIF"]:
        return True

    # DO NOT SKIP, images or pdfs from case-studies have description and title
    # fields those are needed to be translated (or at least to be copied)
    # skip by string in path
    # skip_path_items = ['.jpg','.pdf','.png']
    # obj_url = obj.absolute_url()
    # if any(skip_item in obj_url for skip_item in skip_path_items):
    # return True

    # TODO: add here archived and other rules
    return False


def translations_status_by_version(site, version=0, language=None):
    """Show the list of urls of a version and language"""
    if language is None:
        return "Missing language."

    path = "/cca/" + language
    version = int(version)
    catalog = site.portal_catalog
    brains = catalog.searchResults()
    brains = catalog.searchResults(path=path)

    res = []
    template = "<p>{}</p>"

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, "version", 0))

        if obj_version != version:
            continue

        res.append(template.format(obj.absolute_url()))

    return "".join(res)


def translations_status(site, language=None):
    if language is None:
        return "Missing language."

    path = "/cca/" + language
    catalog = site.portal_catalog
    brains = catalog.searchResults(path=path)

    versions = defaultdict(int)
    template = "<p>{} at version {}</p>"
    logger.info("Translations status:")

    for brain in brains:
        obj = brain.getObject()
        obj_version = int(getattr(obj, "version", 0))
        versions[obj_version] += 1

    res = []
    for k, v in versions.items():
        res.append(template.format(v, k))

    logger.info(res)
    return "".join(res)


class TranslationStatus(BrowserView):
    """Display the the current versions for all translated objects"""

    def __call__(self, **kwargs):
        kwargs.update(self.request.form)

        if "version" in kwargs:
            return translations_status_by_version(getSite(), **kwargs)

        return translations_status(getSite(), **kwargs)


class FindContentWithBlock(BrowserView):
    """ Find the content that has a particular block
    """

    def __call__(self):
        catalog = self.context.portal_catalog
        path = "/".join(self.context.getPhysicalPath())
        brains = catalog.searchResults(path=path, sort_on="path")
        block_type = self.request.form['type']

        found = []
        for brain in brains:
            obj = brain.getObject()
            types = set()
            bt = BlockType(obj, types)
            traverser = BlocksTraverser(obj)
            traverser(bt)
            if block_type in types:
                found.append(obj)

        return "\n".join([o.absolute_url() for o in found])
