"""Translation views"""

from plone.transformchain.interfaces import DISABLE_TRANSFORM_REQUEST_KEY
import base64
import json
import logging
import os
import re
import sys
import traceback
from urllib.parse import unquote

from plone import api
from plone.api import portal
from plone.api.env import adopt_user
from plone.uuid.interfaces import IUUID
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.dexterity.utils import iterSchemata
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five.browser import BrowserView
from zope.interface import alsoProvides
from zope.schema import getFieldsInOrder

from eea.climateadapt.versions import ISerialId

from .constants import LANGUAGE_INDEPENDENT_FIELDS
from .core import (
    ETRANSLATION_API_VERSION,
    call_etranslation_service,
    check_token_security,
    get_blocks_as_html,
    ingest_html,
    queue_job,
    setup_translation_object,
    sync_translation_paths,
    get_content_from_html,
    save_field_data,
)
from .utils import get_value_representation

logger = logging.getLogger("eea.climateadapt.translation")
env = os.environ.get

IS_JOB_EXECUTOR = env("IS_JOB_EXECUTOR", False)

# eTranslation's REST v2 schema caps callerInformation.externalReference at 200
# characters; longer values are rejected with errorCode=-10003.
EXTERNAL_REFERENCE_MAX_LENGTH = 200

# de, fr, pt-BR, sr-Latn. Deliberately a shape check rather than a lookup
# against the site's language list: a malformed code makes eTranslation reject
# the whole request, and once a request carries every target language one typo
# would lose all of them.
LANG_CODE_RE = re.compile(r"^[a-z]{2}(?:-[a-z]{2,4})?$")


def parse_target_langs(value):
    """Normalize a target_lang form value into a list of language codes.

    Accepts the legacy single value ("de"), a comma separated list
    ("de, fr,es") and a repeated form field (["de", "fr"]). Sending every
    target language in one eTranslation request counts as a single active
    submission against the service's concurrency quota, instead of one
    submission per language.

    Malformed codes are dropped rather than passed through, and duplicates are
    collapsed.
    """

    if isinstance(value, (list, tuple)):
        chunks = [str(item) for item in value]
    else:
        chunks = [str(value or "")]

    langs = []
    rejected = []
    for chunk in chunks:
        for language in chunk.split(","):
            language = language.strip().lower()
            if not language:
                continue
            if LANG_CODE_RE.match(language):
                if language not in langs:
                    langs.append(language)
            else:
                rejected.append(language)

    if rejected:
        logger.warning(
            "event=etranslation.target_lang.invalid rejected=%s accepted=%s",
            rejected,
            langs,
        )

    return langs


class IsJobExecutor(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True

        if IS_JOB_EXECUTOR:
            return "true"
        else:
            return "false"


class SaveTranslationHtml(BrowserView):
    """A special view to allow manually submit an HTML translated by
    eTranslation, but that wasn't properly submitted through the callback"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

        request = self.request
        check_token_security(request)

        with adopt_user(username="admin"):
            try:
                html = request.form.get("html", "")
                path = unquote(request.form.get("path", ""))
                language = request.form.get("language", "")
                serial_id = request.form.get("serial_id", 0)
                obj_uid = request.form.get("obj_uid", "")

                site_portal = portal.getSite()
                if path[0] == "/":
                    path = path[1:]
            except Exception as e:
                result = {"error_type": exception_to_json(e)}
                return json.dumps(result)

            try:
                en_obj = site_portal.unrestrictedTraverse(path)
            except KeyError:
                # canonical object was removed
                logger.warning(
                    "Canonical object was removed for save translation: %s", path
                )
                # self.request.response.setHeader("Content-Type", "application/json")
                return json.dumps({"status": "canonical object removed"})

            try:
                canonical_serial_id = int(ISerialId(en_obj).serial_id)

                if obj_uid:
                    current_uid = IUUID(en_obj, None)
                    if current_uid != obj_uid:
                        logger.warning(
                            "UID mismatch for %s: expected %s, got %s. Object was replaced.",
                            path,
                            obj_uid,
                            current_uid,
                        )
                        return json.dumps(
                            {"status": "skipped", "reason": "object_replaced"}
                        )

                if int(canonical_serial_id) != int(serial_id):
                    self.request.response.setHeader("Content-Type", "application/json")
                    result = {"error_type": "mismatched serial id"}
                    return json.dumps(result)

                trans_obj = setup_translation_object(en_obj, language, request)
                ingest_html(trans_obj, html)
                result = {"url": trans_obj.absolute_url()}
            except Exception as e:
                logger.exception("Error in saving translation: \n: %s", e)
                result = {"error_type": exception_to_json(e)}

        # self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(result)


class TranslationCallback(BrowserView):
    """This view is called by the EC translation service.
    Saves the translation in Annotations (or directly in the object in case
    of html fields).
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

        try:
            content_type = self.request.getHeader("Content-Type", "")
            if "application/json" in content_type:
                data = self._parse_rest_v2_callback()
            else:
                data = self._parse_legacy_callback()
        except Exception as e:
            logger.exception("event=etranslation.callback.error error=%s", e)
            return json.dumps({"error_type": exception_to_json(e)})

        opts = {
            "delay": 0,  # Delay in milliseconds
            "priority": 1,
            "attempts": 1,
            "lifo": False,  # we use FIFO queing
        }

        queue_job("save_etranslation", "save_translated_html", data, opts)
        logger.info(
            "event=etranslation.callback.queue_save obj_path=%s html_length=%s",
            data.get("obj_path"),
            len(data.get("html", "")),
        )

        return json.dumps({"status": "ok"})

    def _parse_rest_v2_callback(self):
        body = self.request._file.read()
        payload = json.loads(body.decode("utf-8"))

        request_id = payload.get("requestId")
        source_language = payload.get("sourceLanguage")
        target_language = payload.get("targetLanguage")
        output_format = payload.get("outputFormat")
        extref = payload.get("externalReference")
        result = payload.get("result")
        error_code = payload.get("errorCode")
        error_message = payload.get("errorMessage")

        logger.info(
            "event=etranslation.callback.received api=rest_v2 request_id=%s "
            "source_language=%s target_language=%s output_format=%s "
            "external_reference=%s has_result=%s error_code=%s error_message=%s",
            request_id,
            source_language,
            target_language,
            output_format,
            extref,
            bool(result),
            error_code,
            error_message,
        )

        if error_code or error_message:
            raise ValueError(
                "REST v2 eTranslation callback error: requestId=%s "
                "errorCode=%s errorMessage=%s" % (request_id, error_code, error_message)
            )

        if not extref:
            raise ValueError("REST v2 eTranslation callback missing externalReference")

        if not result:
            raise ValueError("REST v2 eTranslation callback missing result")

        decoded_bytes = base64.b64decode(result)
        html = decoded_bytes.decode("utf-8")

        logger.info(
            "event=etranslation.callback.decoded api=rest_v2 request_id=%s "
            "external_reference=%s html_length=%s",
            request_id,
            extref,
            len(html),
        )

        # A single request may carry several target languages, in which case
        # eTranslation delivers one result per language, all sharing the same
        # externalReference. The language therefore has to travel with the
        # result - it cannot be recovered from externalReference alone.
        data = {"obj_path": extref, "html": html}
        if target_language:
            data["language"] = target_language.lower()

        logger.info(
            "event=etranslation.callback.language api=rest_v2 request_id=%s "
            "language=%s external_reference=%s",
            request_id,
            data.get("language"),
            extref,
        )

        return data

    def _parse_legacy_callback(self):
        # for some reason this request acts strange
        # qs = self.request["QUERY_STRING"]
        # parsed = parse_qs(qs)
        # form = {}
        # for name, val in list(parsed.items()):
        #     form[name] = val[0]
        #
        file_body = self.request._file.read()
        form = self.request.form
        # file_body = form.get("file", "")

        decoded_bytes = base64.b64decode(file_body)
        html = decoded_bytes.decode("utf-8")  # latin-1
        extref = form.get("external-reference")

        logger.info(
            "event=etranslation.callback.received api=legacy "
            "external_reference=%s html_length=%s",
            extref,
            len(html),
        )

        if not extref:
            raise ValueError("Legacy eTranslation callback missing external-reference")

        data = {"obj_path": extref, "html": html}
        legacy_lang = form.get("target-language")
        if legacy_lang:
            data["language"] = legacy_lang.lower()

        return data


class TranslationFailure(BrowserView):
    """Receives eTranslation's failure notification for a submission.

    eTranslation only reports failures when the request asks for them through
    notifications.failure.http. Without it, a language that fails simply never
    delivers and nothing in the system learns why - the only symptom is that a
    submission slot stays occupied until its lease expires.

    This view only records the event and queues it. The async worker owns the
    in-flight gate and can free the slot immediately.
    """

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

        try:
            data = self._parse()
        except Exception as e:
            logger.exception("event=etranslation.failure.parse_error error=%s", e)
            # Always answer 200. A notification we cannot parse will not
            # improve on retry, and eTranslation retries anything that is not
            # 200 - three times, with back-off, for nothing.
            return json.dumps({"status": "ignored", "error_type": exception_to_json(e)})

        opts = {
            "delay": 0,
            "priority": 1,
            "attempts": 1,
            "lifo": False,
        }
        queue_job("save_etranslation", "translation_failed", data, opts)

        logger.info(
            "event=etranslation.failure.queue request_id=%s ext_ref=%s "
            "target_languages=%s error_code=%s error_message=%s",
            data.get("request_id"),
            data.get("obj_path"),
            data.get("languages"),
            data.get("error_code"),
            data.get("error_message"),
        )

        return json.dumps({"status": "ok"})

    def _parse(self):
        body = self.request._file.read()
        payload = json.loads(body.decode("utf-8"))

        extref = payload.get("externalReference")
        if not extref:
            raise ValueError(
                "eTranslation failure notification without externalReference"
            )

        langs = payload.get("targetLanguages") or []
        if isinstance(langs, str):
            langs = [langs]

        return {
            # obj_path keeps the same field name the delivery callback uses, so
            # the worker resolves it through the same correlation lookup.
            "obj_path": extref,
            "request_id": payload.get("requestId"),
            "languages": [str(lang).lower() for lang in langs if lang],
            "error_code": payload.get("errorCode"),
            "error_message": payload.get("errorMessage"),
        }


class ToHtml(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True

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

        if self.request.form.get("roundtrip", ""):
            # wrap in a div for roundtripping
            html = f'<div class="ca-translation-roundtrip">{html}</div>'

            fielddata = get_content_from_html(html, language=self.context.language)

            if self.request.form.get("save", "") and fielddata:
                save_field_data(self.context, self.context, fielddata)

            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(fielddata)

        return html

    def get_value(self, name):
        if name == "blocks":
            return get_blocks_as_html(self.context)
        return get_value_representation(self.context, name)


class CallETranslation(BrowserView):
    """Call eTranslation, triggered by job from worker"""

    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

        check_token_security(self.request)
        form = self.request.form
        html = form.get("html")
        target_lang = form.get("target_lang")
        obj_path = form.get("obj_path")
        obj_uid = form.get("obj_uid")

        # target_lang may be a single language code or a comma separated list.
        target_langs = parse_target_langs(target_lang)

        # ext_ref is the value sent to eTranslation as
        # callerInformation.externalReference, which is echoed back verbatim in
        # the delivery callback. It is schema limited to 200 characters, so the
        # async worker may pass a short correlation id here instead of the long
        # obj_path. obj_path itself is still used for the staleness checks below.
        ext_ref = form.get("ext_ref") or obj_path or ""

        if not target_langs:
            logger.warning("No target languages supplied for %s", obj_path)
            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps({"error_type": "no target languages supplied"})

        if len(ext_ref) > EXTERNAL_REFERENCE_MAX_LENGTH:
            logger.warning(
                "event=etranslation.external_reference.too_long length=%s "
                "limit=%s ext_ref=%s obj_path=%s - eTranslation will reject this "
                "request with errorCode=-10003",
                len(ext_ref),
                EXTERNAL_REFERENCE_MAX_LENGTH,
                ext_ref,
                obj_path,
            )

        # Check if the job is stale
        if "?" in obj_path:
            path, qs = obj_path.split("?", 1)
            from urllib.parse import parse_qs

            params = parse_qs(qs)
            serial_id = params.get("serial_id", [0])[0]
        else:
            path = obj_path
            serial_id = 0

        site = portal.get()
        if path.startswith("/"):
            path = path[1:]

        try:
            obj = site.unrestrictedTraverse(path)

            if obj_uid:
                current_uid = IUUID(obj, None)
                if current_uid != obj_uid:
                    logger.info(
                        "Skipping translation for %s: UID mismatch (object replaced)",
                        path,
                    )
                    self.request.response.setHeader("Content-Type", "application/json")
                    return json.dumps(
                        {
                            "transId": "skipped",
                            "status": "skipped",
                            "reason": "object_replaced",
                        }
                    )

            current_serial = int(ISerialId(obj).serial_id)
            if int(current_serial) > int(serial_id):
                logger.info(
                    "Skipping translation for %s because serial_id mismatch %s != %s",
                    path,
                    current_serial,
                    serial_id,
                )
                self.request.response.setHeader("Content-Type", "application/json")
                return json.dumps(
                    {
                        "transId": "skipped",
                        "status": "skipped",
                        "reason": "stale serial_id",
                    }
                )
        except Exception:
            # If we can't find the object or serial ID, we might as well proceed
            # or log usage. Proceeding is safer to avoid blocking if traverse fails
            # for some reason but path is valid for eTranslation (unlikely).
            pass

        logger.info(
            "event=etranslation.call.dispatch api=%s obj_path=%s ext_ref=%s "
            "target_languages=%s target_language_count=%s",
            ETRANSLATION_API_VERSION,
            obj_path,
            ext_ref,
            target_langs,
            len(target_langs),
        )

        try:
            data = call_etranslation_service(html, ext_ref, target_langs)
        except Exception as e:
            logger.exception("Error in calling eTranslation service: %s", e)
            result = {"error_type": exception_to_json(e)}
            self.request.response.setHeader("Content-Type", "application/json")
            return json.dumps(result)

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
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

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
                    self.request,
                    form.get("expected_uid"),
                )
        except Exception as e:
            result = {"error_type": exception_to_json(e)}

        self.request.response.setHeader("Content-Type", "application/json")
        return json.dumps(result)


class DeleteTranslation(BrowserView):
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        self.request.environ["HTTP_X_THEME_DISABLED"] = "1"
        self.request.environ[DISABLE_TRANSFORM_REQUEST_KEY] = True
        self.request.response.setHeader("Content-Type", "application/json")

        check_token_security(self.request)

        uids_json = self.request.form.get("uids", "[]")
        try:
            uids = json.loads(uids_json)
        except Exception:
            return json.dumps({"error": "Invalid JSON"})

        deleted = []
        errors = []

        with adopt_user(username="admin"):
            for uid in uids:
                try:
                    obj = api.content.get(UID=uid)
                    if obj:
                        path = obj.absolute_url()
                        api.content.delete(obj=obj, check_linkintegrity=False)
                        deleted.append(path)
                        logger.info("Async deleted translation: %s", path)
                except Exception as e:
                    errors.append(f"{uid}: {str(e)}")
                    logger.error("Failed to async delete %s: %s", uid, e)

        return json.dumps({"deleted": deleted, "errors": errors})
