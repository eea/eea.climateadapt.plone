import logging

from BTrees.OIBTree import OIBTree
from persistent.list import PersistentList
from plone.app.multilingual.dx.interfaces import IDexterityTranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.dexterity.interfaces import IDexterityContainer
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides

from eea.climateadapt.translation.core import find_untranslated, queue_translate
from eea.climateadapt.utils import force_unlock

from .utils import get_site_languages

logger = logging.getLogger("eea.climateadapt.translation")


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj_url = self.context.absolute_url()
        language = self.request.form.get("language", None)

        queue_translate(self.context, language)

        return self.request.response.redirect(obj_url)


class TranslateMissing(BrowserView):
    """A view to trigger the translation for missing translations"""

    blacklist = [
        "Image",
        "File",
        "LRF",
        "LIF",
        "Subsite",
        "FrontpageSlide",
    ]

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
            review_state="published",
        )

        result = []

        for i, brain in enumerate(brains):
            obj = brain.getObject()
            if brain.portal_type in self.blacklist:
                continue
            if "sandbox" in obj.absolute_url():
                continue

            langs = find_untranslated(obj, get_site_languages())
            result.append((brain, langs))

            force_unlock(obj)
            url = obj.absolute_url()
            for language in langs:
                logger.info("Queuing %s for translation for %s", url, language)

                queue_translate(obj, language)

        return "ok"


class TranslateFolderAsync(BrowserView):
    """Exposed in /see_folder_objects"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            sort="path",
        )
        lang = self.request.form.get("language", None)

        for i, brain in enumerate(brains):
            obj = brain.getObject()
            if "sandbox" in obj.absolute_url():
                continue

            if lang is None:
                langs = find_untranslated(obj, get_site_languages())
            else:
                langs = [lang]

            force_unlock(obj)
            for language in langs:
                url = obj.absolute_url()
                logger.info("Queuing %s for translation for %s", url, language)

                queue_translate(obj, language)

            # if i % 20 == 0:
            #     transaction.commit()

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        return self.request.response.redirect(self.context.absolute_url())


class FixFolderOrder(BrowserView):
    ORDER_KEY = "plone.folder.ordered.order"
    POS_KEY = "plone.folder.ordered.pos"

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        path = "/".join(self.context.getPhysicalPath())
        brains = self.context.portal_catalog.searchResults(
            sort_on="path", path=path)

        for brain in brains:
            obj = brain.getObject()
            base_path = obj.getPhysicalPath()
            if not IDexterityTranslatable.providedBy(obj):
                continue

            if not IDexterityContainer.providedBy(obj):
                continue

            language = obj.language

            if language is None:
                logger.warning(
                    "Language is set to None for %s", "/".join(
                        obj.getPhysicalPath())
                )
                continue

            canonical = ITranslationManager(obj).get_translation("en")

            if canonical:
                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                annotations = IAnnotations(canonical)
                trans_annot = IAnnotations(obj)

                self.fix_order(
                    obj, canonical, annotations, trans_annot, language, base_path
                )
                self.fix_pos(
                    obj, canonical, annotations, trans_annot, language, base_path
                )

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
                        logger.warning(
                            "Object not translatable: %s",
                            "/".join(other.getPhysicalPath()),
                        )
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
                                base_path,
                                "/".join(trans.getPhysicalPath()),
                            )
                    else:
                        logger.info(
                            "Original without translation: %s (%s)",
                            "/".join(other.getPhysicalPath()),
                            language,
                        )

            for key in (
                orig_order_set
            ):  # append remaining keys that were not found in canonical
                trans_order.append(key)

            if trans_order:
                trans_annot[self.ORDER_KEY] = trans_order
                logger.info(
                    "Fixed order for %s. Old: %r. New: %r",
                    "/".join(obj.getPhysicalPath()),
                    orig_order,
                    list(trans_order),
                )

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
            for id, position in list(proper_pos.items()):
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
                        logger.warning(
                            "Object not translatable: %s",
                            "/".join(other.getPhysicalPath()),
                        )
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
                                base_path,
                                "/".join(trans.getPhysicalPath()),
                            )
                    else:
                        logger.info(
                            "Original without translation: %s (%s)",
                            "/".join(other.getPhysicalPath()),
                            language,
                        )

            # TODO: add missing pos from original
            for k in orig_order_set:
                if k not in trans_pos:
                    trans_pos[k] = orig_pos[k]
            if trans_pos:
                trans_annot[self.POS_KEY] = trans_pos
                logger.info(
                    "Fixed position for %s. Old: %r. New: %r",
                    "/".join(obj.getPhysicalPath()),
                    orig_pos,
                    dict(trans_pos),
                )


class SeeTranslationStatus(BrowserView):
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
        untranslated = set(get_site_languages())

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
            review_state="published",
        )

        result = []

        for i, brain in enumerate(brains):
            if brain.portal_type in self.blacklist:
                continue
            obj = brain.getObject()
            langs = self.find_untranslated(obj)
            result.append((brain, langs))

        return result
