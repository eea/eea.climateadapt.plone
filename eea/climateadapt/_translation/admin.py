"""Admin translation"""

import logging

import transaction
from plone.api import portal
from plone.app.multilingual.interfaces import ITranslationManager
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from eea.climateadapt.blocks import BlocksTraverser, BlockType

from .core import setup_translation_object

logger = logging.getLogger("eea.climateadapt")


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
                        try:
                            trans_obj = setup_translation_object(
                                obj, language, site)
                            logger.info(
                                "Translated object %s %s/%s %s",
                                language,
                                i,
                                brain_count,
                                trans_obj.absolute_url(),
                            )
                        except:
                            logger.exception(
                                "Error setting up translation object %s", obj.absolute_url())

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


class ReindexTree(BrowserView):
    def __call__(self):
        path = '/'.join(self.context.getPhysicalPath())
        brains = self.context.portal_catalog.searchResults(
            sort_on='path', path=path)

        total = len(brains)
        for i, brain in enumerate(brains):
            # if brain.Title:
            #     continue

            obj = brain.getObject()
            logger.info("Reindexing %s of %s: %s", i, total,
                        "/".join(obj.getPhysicalPath()))
            obj.reindexObject(idxs=["object_provides", "Language"])
            if i % 10 == 0:
                transaction.savepoint()

        return "ok"


class SetTreeLanguage(BrowserView):

    def __call__(self):
        path = '/'.join(self.context.getPhysicalPath())
        brains = self.context.portal_catalog.searchResults(
            sort_on='path', path=path
        )

        language = self.request.form.get('language', 'en')

        total = len(brains)
        for i, brain in enumerate(brains):
            obj = brain.getObject()
            obj.language = language
            obj._p_changed = True
            obj.reindexObject(
                idxs=["Language", "TranslationGroup", "object_provides"])
            logger.info("Reindexing %s of %s: %s", i, total,
                        "/".join(obj.getPhysicalPath()))
            if i % 10 == 0:
                transaction.savepoint()

        return "ok"
