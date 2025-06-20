"""Translation views"""

import base64
import json
import logging
import os
import sys
import traceback

from plone.api import portal
from plone.api.env import adopt_user
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.utils import iterSchemata
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from eea.climateadapt.versions import ISerialId

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import (
    call_etranslation_service,
    check_token_security,
    get_blocks_as_html,
    ingest_html,
    queue_job,
    setup_translation_object,
    sync_translation_paths,
)
from .utils import get_value_representation

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get

IS_JOB_EXECUTOR = env("IS_JOB_EXECUTOR", False)


class IsJobExecutor(BrowserView):
    def __call__(self):
        if IS_JOB_EXECUTOR:
            return "true"
        else:
            return "false"


class SaveTranslationHtml(BrowserView):
    """A special view to allow manually submit an HTML translated by
    eTranslation, but that wasn't properly submitted through the callback"""

    def __call__(self):
        request = self.request
        check_token_security(request)
        html = request.form.get("html", "")
        path = request.form.get("path", "")
        language = request.form.get("language", "")
        serial_id = request.form.get("serial_id", 0)

        site_portal = portal.getSite()
        if path[0] == "/":
            path = path[1:]

        try:
            en_obj = site_portal.unrestrictedTraverse(path)
            canonical_serial_id = ISerialId(en_obj)

            if int(canonical_serial_id) != int(serial_id):
                return json.dumps({"error_type": "mismatched serial id"})

            with adopt_user(username="admin"):
                trans_obj = setup_translation_object(en_obj, language, request)
                ingest_html(trans_obj, html)
                result = {"url": trans_obj.absolute_url()}
        except Exception as e:
            logger.exception("Error in saving translation: \n: %s", e)
            result = {"error_type": exception_to_json(e)}

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(result)


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
        opts = {
            "delay": 0,  # Delay in milliseconds
            "priority": 1,
            "attempts": 1,
            "lifo": False,  # we use FIFO queing
        }

        queue_job("save_etranslation", "save_translated_html", data, opts)

        return "ok"


class ToHtml(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"

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
        check_token_security(self.request)
        form = self.request.form
        html = form.get("html")
        target_lang = form.get("target_lang")
        obj_path = form.get("obj_path")

        print("calling etranslation")
        data = call_etranslation_service(html, obj_path, [target_lang])
        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(data)


def exception_to_json(exception):
    # Get the exception information
    exc_type, exc_value, exc_traceback = sys.exc_info()

    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    tb_text = "".join(tb_lines)

    exception_dict = {
        "type": exc_type.__name__,
        "message": str(exc_value),
        "traceback": tb_text,
    }

    return exception_dict

    # return json.dumps(exception_dict, indent=4)


class SyncTranslatedPaths(BrowserView):
    """Call eTranslation, triggered by job from worker"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        check_token_security(self.request)

        form = self.request.form
        langs = form.get("langs", [])
        if langs:
            langs = langs.split(",")

        try:
            with adopt_user(username="admin"):
                result = sync_translation_paths(
                    form["oldParent"],
                    form["oldName"],
                    form["newParent"],
                    form["newName"],
                    langs,
                )
        except Exception as e:
            result = {"error_type": exception_to_json(e)}

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(result)
