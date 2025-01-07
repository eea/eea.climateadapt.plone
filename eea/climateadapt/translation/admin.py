"""Admin translation"""

import logging

import transaction
from BTrees.OIBTree import OIBTree
from persistent.list import PersistentList
from plone.api import portal
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.interfaces import IDexterityContainer
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.annotation.interfaces import IAnnotations

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
        from zc.async.queue import Queue
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


class FixFolderOrder(BrowserView):

    ORDER_KEY = "plone.folder.ordered.order"
    POS_KEY = "plone.folder.ordered.pos"

    def __call__(self):
        path = '/'.join(self.context.getPhysicalPath())
        brains = self.context.portal_catalog.searchResults(
            sort_on='path', path=path
        )

        for brain in brains:
            obj = brain.getObject()
            base_path = obj.getPhysicalPath()
            if not IDexterityTranslatable.providedBy(obj):
                continue

            if not IDexterityContainer.providedBy(obj):
                continue

            language = obj.language

            if language is None:
                logger.warning("Language is set to None for %s",
                               "/".join(obj.getPhysicalPath()))
                continue

            canonical = ITranslationManager(obj).get_translation("en")

            if canonical:
                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                self.fix_order(obj, canonical, annotations,
                               trans_annot, language, base_path)
                self.fix_pos(obj, canonical, annotations,
                             trans_annot, language, base_path)

        return "done"

    def fix_order(self, obj, canonical, annotations, trans_annot, language, base_path):
        tree = obj._tree
        obj_ids = list(tree.keys())

        # order is a list like: ['index_html', 'organisations', 'international']
        proper_order = list(annotations.get(self.ORDER_KEY, []))
        orig_order = list(trans_annot.get(self.ORDER_KEY, []))

        if proper_order != orig_order:
            trans_order = PersistentList()
            # rebuild the order
            orig_order_set = set(orig_order)
            for id in proper_order:
                if id in obj_ids:
                    trans_order.append(id)
                    if id in orig_order_set:
                        orig_order_set.remove(id)
                else:
                    # was the object translated with another id?
                    other = canonical._getOb(id)
                    try:
                        trans = ITranslationManager(
                            other).get_translation(language)
                    except TypeError:
                        logger.warning("Object not translatable: %s",
                                       "/".join(other.getPhysicalPath()))
                        continue
                    if trans:
                        test_path = trans.getPhysicalPath()[:-1]

                        if test_path == base_path:
                            new_id = trans.getId()
                            if new_id in orig_order_set:
                                orig_order_set.remove(new_id)
                            trans_order.append(new_id)
                        else:
                            logger.warning(
                                "Translated object is in another folder: %s (should be: %s )",
                                base_path, "/".join(trans.getPhysicalPath()))
                    else:
                        logger.info("Original without translation: %s (%s)",
                                    "/".join(other.getPhysicalPath()), language)

            for key in orig_order_set:      # append remaining keys that were not found in canonical
                trans_order.append(key)

            if trans_order:
                trans_annot[self.ORDER_KEY] = trans_order
                logger.info("Fixed order for %s. Old: %r. New: %r",
                            "/".join(obj.getPhysicalPath()), orig_order, list(trans_order))

    def fix_pos(self, obj, canonical, annotations, trans_annot, language, base_path):
        tree = obj._tree
        obj_ids = list(tree.keys())

        # pos is a mapping like: {'index_html': 0, 'international': 2, 'organisations': 1}
        proper_pos = dict(annotations.get(self.POS_KEY, {}))
        orig_pos = dict(trans_annot.get(self.POS_KEY, {}))

        if proper_pos != orig_pos:
            trans_pos = OIBTree()
            # rebuild the order
            orig_order_set = set(orig_pos.keys())
            for (id, position) in proper_pos.items():
                if id in obj_ids:
                    trans_pos[id] = position
                    if id in orig_order_set:
                        orig_order_set.remove(id)
                else:
                    # was the object translated with another id?
                    other = canonical._getOb(id)
                    try:
                        trans = ITranslationManager(
                            other).get_translation(language)
                    except TypeError:
                        logger.warning("Object not translatable: %s",
                                       "/".join(other.getPhysicalPath()))
                        continue
                    if trans:
                        test_path = trans.getPhysicalPath()[:-1]

                        if test_path == base_path:
                            new_id = trans.getId()
                            if new_id in orig_order_set:
                                orig_order_set.remove(new_id)
                            trans_pos[new_id] = position
                        else:
                            logger.warning(
                                "Translated object is in another folder: %s (should be: %s )",
                                base_path, "/".join(trans.getPhysicalPath()))
                    else:
                        logger.info("Original without translation: %s (%s)",
                                    "/".join(other.getPhysicalPath()), language)

            # TODO: add missing pos from original
            for k in orig_order_set:
                if k not in trans_pos:
                    trans_pos[k] = orig_pos[k]
            if trans_pos:
                trans_annot[self.POS_KEY] = trans_pos
                logger.info("Fixed position for %s. Old: %r. New: %r",
                            "/".join(obj.getPhysicalPath()), orig_pos, dict(trans_pos))


class SeeTranslationStatus(BrowserView):

    good_lang_codes = ["fr", "de", "it", "es", "pl"]
    blacklist = [
        "Image",
        "File",
        "LRF",
        "LIF",
        "Subsite",
        "FrontpageSlide",
    ]

    def find_untranslated(self, obj):
        tm = ITranslationManager(obj)
        translations = tm.get_translations()
        untranslated = set(self.good_lang_codes)

        for langcode, obj in translations.items():
            if langcode == "en":
                continue
            if obj.title and langcode in untranslated:
                untranslated.remove(langcode)

        return list(untranslated)

    def brains(self):

        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            review_state="published"
        )

        result = []

        for i, brain in enumerate(brains):
            if brain.portal_type in self.blacklist:
                continue
            obj = brain.getObject()
            langs = self.find_untranslated(obj)
            result.append((brain, langs))

        return result
