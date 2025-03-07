"""Translation views"""

import base64
import json
import logging
import os
# from urllib.parse import parse_qs

from eea.climateadapt.versions import ISerialId
from plone.api import portal
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.utils import iterSchemata
from Products.Five.browser import BrowserView
from zope.schema import getFieldsInOrder

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import (
    call_etranslation_service,
    check_token_security,
    get_blocks_as_html,
    ingest_html,
    queue_job,
    setup_translation_object,
)
from .utils import get_value_representation

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
        check_token_security(self.request)
        html = self.request.form.get("html", "")  # .decode("utf-8")
        path = self.request.form.get("path", "")
        language = self.request.form.get("language", "")
        serial_id = self.request.form.get("serial_id", 0)

        site_portal = portal.getSite()
        if path[0] == "/":
            path = path[1:]

        en_obj = site_portal.unrestrictedTraverse(path)
        canonical_serial_id = ISerialId(en_obj)

        if int(canonical_serial_id) != int(serial_id):
            return "mismatched serial id"

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
        # qs = self.request["QUERY_STRING"]
        # parsed = parse_qs(qs)
        # form = {}
        # for name, val in list(parsed.items()):
        #     form[name] = val[0]
        #
        _file = self.request._file.read()
        form = self.request.form
        # _file = form.get("file", "")

        decoded_bytes = base64.b64decode(_file)
        html = decoded_bytes.decode("utf-8")  # latin-1
        # html = html_translated.encode("utf-8")

        extref = form.get("external-reference")

        # logger.info("Translation Callback Incoming file: %s" % _file)
        # logger.info("Translate volto html form: %s", form)
        # logger.info("Translate volto html: %s", html_translated)

        data = {"obj_path": extref, "html": html}
        # print("data", data)
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
        return get_value_representation(self.context, name)


class CallETranslation(BrowserView):
    """Call eTranslation, triggered by job from worker"""

    def __call__(self):
        # TODO: add security check
        check_token_security(self.request)
        form = self.request.form
        html = form.get("html")
        target_lang = form.get("target_lang")
        obj_path = form.get("obj_path")

        print("calling etranslation")
        data = call_etranslation_service(html, obj_path, [target_lang])
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(data)
