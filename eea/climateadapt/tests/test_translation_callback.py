"""Regression tests for the eTranslation callback's HTTP status decisions.

eTranslation retries an HTTP callback up to 3 times with exponential back-off,
but only on 5xx. 4xx is never retried. TranslationCallback used to return HTTP
200 for every outcome, including its own internal failures - so a transient
fault on our side (Redis unavailable, a handler bug) was reported to the
platform as a successful delivery, the retry budget was forfeited, and a
translation eTranslation had already produced was lost silently.

That is a strong candidate for the "silent language drops" that have been
attributed to upstream flakiness. These tests pin the status mapping.

See artifacts/etranslation-docs/README.md for the documented retry policy.
"""

import unittest

from eea.climateadapt.translation.views import (
    CallbackDeliveryError,
    CallbackPayloadError,
    callback_failure_response,
)


class TestCallbackFailureStatus(unittest.TestCase):
    def test_internal_error_is_5xx_so_it_gets_retried(self):
        """The regression: a plain exception must NOT be a silent 200."""
        try:
            raise ValueError("Redis connection lost")
        except ValueError as exc:
            status, body = callback_failure_response(exc)
        self.assertEqual(status, 503)
        self.assertIn("error_type", body)
        self.assertEqual(body["error_type"]["type"], "ValueError")

    def test_unexpected_runtime_error_is_5xx(self):
        try:
            raise RuntimeError("queue backend down")
        except RuntimeError as exc:
            status, _ = callback_failure_response(exc)
        self.assertEqual(status, 503)

    def test_payload_error_is_4xx_and_not_retried(self):
        """Malformed payloads are identical on every retry - do not retry."""
        try:
            raise CallbackPayloadError("missing externalReference")
        except CallbackPayloadError as exc:
            status, body = callback_failure_response(exc)
        self.assertEqual(status, 400)
        self.assertEqual(body["status"], "rejected")

    def test_missing_result_is_4xx(self):
        try:
            raise CallbackPayloadError("callback missing result")
        except CallbackPayloadError as exc:
            status, _ = callback_failure_response(exc)
        self.assertEqual(status, 400)

    def test_delivery_error_is_acknowledged_not_retried(self):
        """An error notification carries nothing new; retrying it is pointless,
        but it must be recorded rather than swallowed."""
        try:
            raise CallbackDeliveryError(
                "requestId=1 errorCode=-1 targetLanguage=EL externalReference=x"
            )
        except CallbackDeliveryError as exc:
            status, body = callback_failure_response(exc)
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "error-recorded")
        self.assertIn("EL", body["error"])

    def test_subclasses_of_payload_error_stay_4xx(self):
        class Detailed(CallbackPayloadError):
            pass

        try:
            raise Detailed("bad json")
        except CallbackPayloadError as exc:
            status, _ = callback_failure_response(exc)
        self.assertEqual(status, 400)

    def test_delivery_error_is_not_confused_with_payload_error(self):
        """Both are ValueError-free; the mapping must distinguish them."""
        for exc_cls, expected in (
            (CallbackDeliveryError, 200),
            (CallbackPayloadError, 400),
        ):
            try:
                raise exc_cls("x")
            except exc_cls as exc:
                status, _ = callback_failure_response(exc)
            self.assertEqual(status, expected, exc_cls.__name__)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
