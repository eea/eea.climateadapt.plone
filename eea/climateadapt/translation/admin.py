"""Admin translation"""

import logging
from collections import defaultdict

import transaction
from plone.api import portal
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.site.hooks import getSite

from eea.climateadapt.blocks import BlocksTraverser, BlockType

from .core import setup_translation_object

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
    """Find the content that has a particular block"""

    def __call__(self):
        catalog = self.context.portal_catalog
        path = "/".join(self.context.getPhysicalPath())
        brains = catalog.searchResults(path=path, sort_on="path")
        block_type = self.request.form["type"]

        found = []
        for brain in brains:
            obj = brain.getObject()
            if not hasattr(obj.aq_inner.aq_self, "blocks"):
                continue
            types = set()
            bt = BlockType(obj, types)
            traverser = BlocksTraverser(obj)
            traverser(bt)
            if block_type in types:
                found.append(obj)

        return "\n".join([o.absolute_url() for o in found])


def split_list(lst, chunk_size):
    return [lst[i: i + chunk_size] for i in range(0, len(lst), chunk_size)]


class CreateTranslationStructure(BrowserView):
    def __call__(self):
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            object_provides=[
                'plone.app.multilingual.interfaces.ITranslatable'],
            # portal_type="Folder",
            sort_on="path",
        )
        site = portal.getSite()

        languages = [
            "bg",
            "cs",
            "da",
            "el",
            "et",
            "fi",
            "ga",
            "hr",
            "hu",
            "lt",
            "lv",
            "mt",
            "nl",
            "pt",
            "sk",
            "sl",
            "sv",
        ]

        language = self.request.form.get("language", None)

        if language:
            languages = [language]

        brain_count = len(brains)

        for language in languages:
            counted_brains = zip(list(range(len(brains))), brains)
            batched_brains = split_list(counted_brains, 20)

            for batch in batched_brains:

                def task():
                    for i, brain in batch:
                        obj = brain.getObject()
                        logger.info("Setting up %s", obj.absolute_url())
                        if "sandbox" in obj.absolute_url():
                            # we don't translate sandbox objects, too much bother
                            continue
                        trans_obj = setup_translation_object(
                            obj, language, site)
                        logger.info(
                            "Translated object %s %s/%s %s",
                            language,
                            i,
                            brain_count,
                            trans_obj.absolute_url(),
                        )

                transaction.begin()
                task()
                transaction.savepoint()
                # try:
                #     task()
                #     transaction.commit()
                # except Exception:
                #     logger.exception("Exception, but will continue")

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")
        self.request.response.redirect(self.context.absolute_url())


class ResetAsync(BrowserView):
    def __call__(self):
        queue = self.context._p_jar.root()['zc.async']['']
        from zc.async .queue import Queue
        Queue.__init__(queue)
        import transaction
        transaction.commit()
        return "done"
