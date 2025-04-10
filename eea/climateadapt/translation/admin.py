import logging

from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
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
