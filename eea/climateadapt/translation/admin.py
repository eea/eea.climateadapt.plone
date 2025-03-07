import logging

from Products.Five.browser import BrowserView
from plone.app.multilingual.interfaces import ITranslationManager
from Products.statusmessages.interfaces import IStatusMessage
from eea.climateadapt.translation.core import queue_translate
from eea.climateadapt.utils import force_unlock

logger = logging.getLogger("eea.climateadapt.translation")


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj_url = self.context.absolute_url()
        language = self.request.form.get("language", None)

        queue_translate(obj_url, language)

        return self.request.response.redirect(obj_url)


class TranslateMissing(BrowserView):
    """A view to trigger the translation for missing translations"""

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

    def __call__(self):
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

            langs = self.find_untranslated(obj)
            result.append((brain, langs))

            force_unlock(obj)
            url = obj.absolute_url()
            for language in langs:
                logger.info("Queuing %s for translation for %s", url, language)

                queue_translate(obj, language)

        return "ok"


class TranslateFolderAsync(BrowserView):
    """Exposed in /see_folder_objects"""

    good_lang_codes = ["fr", "de", "it", "es", "pl"]

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

    def __call__(self):
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
                langs = self.find_untranslated(obj)
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
