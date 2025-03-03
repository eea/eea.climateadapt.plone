"""Translation views"""

import base64
import cgi
import json
import logging
import os

from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.utils import iterSchemata
from Products.Five.browser import BrowserView
from zope.schema import getFieldsInOrder


from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import (
    call_etranslation_service,
    get_blocks_as_html,
    ingest_html,
    queue_job,
    setup_translation_object,
)
from .utils import get_value_representation

# from urllib.parse import urlparse, parse_qs
# import transaction

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get


class HTMLIngestion(BrowserView):
    """A special view to allow manually submit an HTML translated by
    eTranslation, but that wasn't properly submitted through the callback"""

    def __call__(self):
        html = self.request.form.get("html", "").decode("utf-8")
        path = self.request.form.get("path", "")

        if not (html and path):
            return self.index()

        site = portal.getSite()
        trans_obj = site.unrestrictedTraverse(path)
        ingest_html(trans_obj, html)
        return "ok"


class SaveTranslationHtml(BrowserView):
    """A special view to allow manually submit an HTML translated by
    eTranslation, but that wasn't properly submitted through the callback"""

    def __call__(self):
        html = self.request.form.get("html", "").decode("utf-8")
        path = self.request.form.get("path", "")
        language = self.request.form.get("language", "")

        site_portal = portal.getSite()

        en_obj = site_portal.unrestrictedTraverse(path)
        trans_obj = setup_translation_object(en_obj, language, site_portal)
        ingest_html(trans_obj, html)
        return "ok"


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
        for name, val in list(parsed.items()):
            form[name] = val[0]

        _file = self.request._file.read()

        decoded_bytes = base64.b64decode(_file)
        html_translated = decoded_bytes.decode("latin-1")
        html = html_translated.encode("utf-8")

        extref = form.get("external-reference")

        logger.info("Translation Callback Incoming file: %s" % _file)
        logger.info("Translate volto html form: %s", form)
        logger.info("Translate volto html: %s", html_translated)

        data = {"obj_path": extref, "html": html}
        queue_job("etranslation", "save_translated_html", data)

        return "ok"


class ToHtml(BrowserView):
    def __call__(self):
        obj = self.context

        self.fields = {}
        self.order = []
        self.values = {}

        for schema in iterSchemata(obj):
            for k, v in getFieldsInOrder(schema):
                if (
                    ILanguageIndependentField.providedBy(v)
                    or k in LANGUAGE_INDEPENDENT_FIELDS
                ):
                    continue
                self.fields[k] = v
                value = self.get_value(k)
                if value and k not in self.order:
                    self.order.append(k)
                    self.values[k] = value

        html = self.index()
        return html

    def get_value(self, name):
        if name == "blocks":
            return get_blocks_as_html(self.context)
        # TODO: remove cover_layout related handling
        if name == "cover_layout":
            return None
        #     value = get_cover_as_html(self.context)
        #     return value
        return get_value_representation(self.context, name)


class CallETranslation(BrowserView):
    """Call eTranslation, triggered by job from worker"""

    def __call__(self):
        # TODO: add security check
        form = self.request.form
        html = form.get("html")
        source_lang = form.get("source_lang")
        obj_path = form.get("obj_path")

        data = call_etranslation_service(source_lang, html, obj_path)
        return json.dumps(data)
