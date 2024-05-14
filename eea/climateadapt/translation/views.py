"""Translation views"""

from .core import create_translation_object
import base64
import cgi
import logging
import os

import transaction
from eea.climateadapt.browser.admin import force_unlock
from eea.climateadapt.translation.volto import (
    get_content_from_html,
    translate_volto_html,
)
from plone.api import portal
from plone.app.multilingual.manager import TranslationManager
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import getMultiAdapter

from . import (
    get_translation_key_values,
    get_translation_keys,
    get_translation_report,
)
from .core import (
    copy_missing_interfaces,
    handle_cover_step_4,
    handle_folder_doc_step_4,
    handle_link,
    save_field_data,
)

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get


class TranslationCallback(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations (or directly in the object in case
    of html fields).
    """

    def __call__(self):
        # for some reason this request acts strange
        qs = self.request["QUERY_STRING"]
        parsed = cgi.parse_qs(qs)
        form = {}
        for name, val in parsed.items():
            form[name] = val[0]

        _file = self.request._file.read()
        logger.info("Translation Callback Incoming form: %s" % form)
        logger.info("Translation Callback Incoming file: %s" % _file)

        self.save_html_volto(form, _file)
        return "ok"

    def save_html_volto(self, form, b64_str):
        # file.seek(0)
        # b64_str = file.read()
        html_translated = base64.decodestring(b64_str).decode("latin-1")

        logger.info("Translate volto html form: %s", form)
        logger.info("Translate volto html: %s", html_translated)

        site = portal.getSite()
        trans_obj_path = form.get("external-reference")
        if "https://" in trans_obj_path:
            trans_obj_path = "/cca" + \
                trans_obj_path.split(site.absolute_url())[-1]

        trans_obj = site.unrestrictedTraverse(trans_obj_path)
        force_unlock(trans_obj)

        fielddata = get_content_from_html(html_translated.encode("latin-1"))

        translations = TranslationManager(trans_obj).get_translations()
        en_obj = translations["en"]  # hardcoded, should use canonical

        save_field_data(en_obj, trans_obj, fielddata)

        copy_missing_interfaces(en_obj, trans_obj)

        # layout_en = en_obj.getLayout()
        # if layout_en:
        #     trans_obj.setLayout(layout_en)

        if trans_obj.portal_type == "collective.cover.content":
            handle_cover_step_4(en_obj, trans_obj, trans_obj.language, False)
        if trans_obj.portal_type in ("Folder", "Document"):
            handle_folder_doc_step_4(en_obj, trans_obj, False, False)
        if trans_obj.portal_type in ["Link"]:
            handle_link(en_obj, trans_obj)

        # TODO: sync workflow state

        trans_obj._p_changed = True
        trans_obj.reindexObject()
        logger.info("Html volto translation saved for %s",
                    trans_obj.absolute_url())


class TranslateObjectAsync(BrowserView):
    def __call__(self):
        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")

        obj = self.context
        html = getMultiAdapter(
            (self.context, self.context.REQUEST), name="tohtml")()
        site = portal.getSite()
        http_host = self.context.REQUEST.environ.get(
            "HTTP_X_FORWARDED_HOST", site.absolute_url()
        )
        language = self.request.form.get("language", None)

        translate_volto_html(html, obj, http_host, language)

        self.request.response.redirect(obj.absolute_url())


class TranslateFolderAsync(BrowserView):
    def __call__(self):
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath())
        )
        site = portal.getSite()
        site_url = site.absolute_url()
        language = self.request.form.get("language", None)

        for i, brain in enumerate(brains):
            obj = brain.getObject()

            html = getMultiAdapter(
                (obj, self.context.REQUEST), name="tohtml")()
            http_host = self.context.REQUEST.environ.get(
                "HTTP_X_FORWARDED_HOST", site_url
            )

            translate_volto_html(html, obj, http_host, language)

            if i % 20 == 0:
                transaction.commit()

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")
        self.request.response.redirect(self.context.absolute_url())


def split_list(lst, chunk_size):
    return [lst[i: i + chunk_size] for i in range(0, len(lst), chunk_size)]


class CreateTranslationStructure(BrowserView):
    def __call__(self):
        context = self.context

        brains = context.portal_catalog.searchResults(
            path="/".join(context.getPhysicalPath()),
            portal_type="Folder",
            sort_on="path",
        )
        site = portal.getSite()
        language = self.request.form.get("language", None)
        if not language:
            return "no language"

        languages = [
            # "bg",
            # "hr",
            # "cs",
            # "da",
            # "nl",
            "et",
            "fi",
            "el",
            "hu",
            "ga",
            "lv",
            "lt",
            "mt",
            "pt",
            "sk",
            "sl",
            "sv",
        ]

        brain_count = len(brains)

        for language in languages:
            counted_brains = zip(list(range(len(brains))), brains)
            batched_brains = split_list(counted_brains, 20)

            for batch in batched_brains:

                def task():
                    for i, brain in batch:
                        obj = brain.getObject()
                        trans_obj = create_translation_object(
                            obj, language, site)
                        logger.info(
                            "Translated object %s %s/%s %s",
                            language,
                            i,
                            brain_count,
                            trans_obj.absolute_url(),
                        )

                transaction.begin()
                try:
                    task()
                    transaction.commit()
                except:
                    logger.exception("Will continue")

        messages = IStatusMessage(self.request)
        messages.add("Translation process initiated.", type="info")
        self.request.response.redirect(self.context.absolute_url())


class TranslationList(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations

    Used with multiple templates, registered as /@@translate-list, /@@translate-report, /@@translate-key

    TODO: remove this, no longer needed
    """

    def list(self):
        form = self.request.form
        search = form.get("search", None)
        limit = int(form.get("limit", 10))

        data = get_translation_keys()
        if search:
            data = [item for item in data if search in item]
        if len(data) > limit:
            data = data[0:limit]
        return data

    def keys(self):
        key = self.request.form["key"]
        return get_translation_key_values(key)

    def report(self):
        return get_translation_report()
