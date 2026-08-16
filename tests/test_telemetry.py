import json
import logging
import math
from pathlib import Path
import re
import unittest

from fastapi.testclient import TestClient

from api.config import ALGORITHM_VERSION, ALLOWED_ORIGINS
from api.main import create_app
from api.telemetry import EVENT_FIELDS, safe_event


ANALYSIS_ID = "a" * 32
SECURITY_HEADERS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "camera=(), microphone=(), geolocation=()",
    "content-security-policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    ),
}
EXPECTED_EVENT_FIELDS = {
    "page_viewed": {"device_category", "referrer_category"},
    "analysis_started": {
        "analysis_id",
        "file_type",
        "file_size_bucket",
        "jd_length_bucket",
        "algorithm_version",
    },
    "upload_validation_failed": {
        "analysis_id",
        "error_code",
        "file_type",
        "file_size_bucket",
    },
    "analysis_succeeded": {
        "analysis_id",
        "file_type",
        "processing_ms",
        "algorithm_version",
        "known_count",
        "unknown_count",
        "evidenced_count",
        "uncertain_count",
    },
    "analysis_failed": {
        "analysis_id",
        "error_code",
        "processing_ms",
        "retryable",
    },
    "evidence_viewed": {"analysis_id", "requirement_id", "resume_status"},
    "suggestion_accepted": {"analysis_id", "suggestion_id", "algorithm_version"},
    "suggestion_edited": {
        "analysis_id",
        "suggestion_id",
        "confirmed_pending_facts",
    },
    "suggestion_rejected": {"analysis_id", "suggestion_id", "reason_code"},
    "draft_exported": {
        "analysis_id",
        "format",
        "suggestion_count",
        "pending_count",
    },
    "feedback_submitted": {"analysis_id", "rating", "reason_code"},
}
VALID_EVENTS = {
    "page_viewed": {
        "device_category": "desktop",
        "referrer_category": "direct",
    },
    "analysis_started": {
        "analysis_id": ANALYSIS_ID,
        "file_type": "txt",
        "file_size_bucket": "lt_100kb",
        "jd_length_bucket": "50_199",
        "algorithm_version": ALGORITHM_VERSION,
    },
    "upload_validation_failed": {
        "analysis_id": ANALYSIS_ID,
        "error_code": "FILE_TOO_LARGE",
        "file_type": "pdf",
        "file_size_bucket": "1mb_5mb",
    },
    "analysis_succeeded": {
        "analysis_id": ANALYSIS_ID,
        "file_type": "docx",
        "processing_ms": 12.5,
        "algorithm_version": ALGORITHM_VERSION,
        "known_count": 4,
        "unknown_count": 1,
        "evidenced_count": 3,
        "uncertain_count": 1,
    },
    "analysis_failed": {
        "analysis_id": ANALYSIS_ID,
        "error_code": "ANALYSIS_TIMEOUT",
        "processing_ms": 1200,
        "retryable": True,
    },
    "evidence_viewed": {
        "analysis_id": ANALYSIS_ID,
        "requirement_id": "aa_py",
        "resume_status": "evidenced",
    },
    "suggestion_accepted": {
        "analysis_id": ANALYSIS_ID,
        "suggestion_id": "rw-001",
        "algorithm_version": ALGORITHM_VERSION,
    },
    "suggestion_edited": {
        "analysis_id": ANALYSIS_ID,
        "suggestion_id": "rw-001",
        "confirmed_pending_facts": False,
    },
    "suggestion_rejected": {
        "analysis_id": ANALYSIS_ID,
        "suggestion_id": "rw-001",
        "reason_code": "no_reason",
    },
    "draft_exported": {
        "analysis_id": ANALYSIS_ID,
        "format": "markdown",
        "suggestion_count": 2,
        "pending_count": 1,
    },
    "feedback_submitted": {
        "analysis_id": ANALYSIS_ID,
        "rating": "helpful",
        "reason_code": "no_reason",
    },
}


def log_messages(logger_name: str):
    records = []

    class Capture(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    logger = logging.getLogger(logger_name)
    handler = Capture()
    previous_level = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    class CapturedLogs:
        def __enter__(self):
            return records

        def __exit__(self, exc_type, exc_value, traceback):
            logger.removeHandler(handler)
            logger.setLevel(previous_level)

    return CapturedLogs()


class SafeEventSchemaTests(unittest.TestCase):
    def test_event_dictionary_is_closed_and_exact(self):
        self.assertEqual(EVENT_FIELDS, EXPECTED_EVENT_FIELDS)

    def test_every_event_accepts_its_complete_schema_and_drops_unknown_fields(self):
        for event_name, attributes in VALID_EVENTS.items():
            with self.subTest(event_name=event_name):
                supplied = {
                    **attributes,
                    "resume_text": "private",
                    "jd": "private",
                    "filename": "Jane-Doe-resume.txt",
                }
                original = dict(supplied)

                event = safe_event(event_name, supplied)

                self.assertEqual(
                    event,
                    {"name": event_name, "attributes": attributes},
                )
                self.assertEqual(supplied, original)

    def test_unknown_event_and_non_mapping_attributes_are_rejected(self):
        invalid_calls = (
            ("raw_resume_uploaded", {"file_type": "txt"}),
            (123, {}),
            ("page_viewed", []),
            ("page_viewed", None),
        )
        for event_name, attributes in invalid_calls:
            with self.subTest(event_name=event_name, attributes=attributes):
                with self.assertRaises(ValueError):
                    safe_event(event_name, attributes)

    def test_analysis_id_is_required_except_for_page_viewed(self):
        self.assertEqual(
            safe_event("page_viewed", {}),
            {"name": "page_viewed", "attributes": {}},
        )
        for event_name, attributes in VALID_EVENTS.items():
            if event_name == "page_viewed":
                continue
            with self.subTest(event_name=event_name):
                without_id = dict(attributes)
                without_id.pop("analysis_id")
                with self.assertRaises(ValueError):
                    safe_event(event_name, without_id)

    def test_analysis_and_entity_identifiers_use_closed_safe_patterns(self):
        for invalid_id in (
            "a" * 31,
            "a" * 33,
            "A" * 32,
            "g" * 32,
            "12345678901234567890123456789012@example.com",
        ):
            with self.subTest(analysis_id=invalid_id):
                with self.assertRaises(ValueError):
                    safe_event("analysis_failed", {
                        **VALID_EVENTS["analysis_failed"],
                        "analysis_id": invalid_id,
                    })

        for event_name, field_name in (
            ("evidence_viewed", "requirement_id"),
            ("suggestion_accepted", "suggestion_id"),
        ):
            for valid_id in ("a", "aa_py", "rw-001", "a" * 64):
                with self.subTest(event_name=event_name, valid_id=valid_id):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = valid_id
                    self.assertEqual(
                        safe_event(event_name, attributes)["attributes"][field_name],
                        valid_id,
                    )
            for invalid_id in ("", "Upper", "has space", "a.b", "a" * 65):
                with self.subTest(event_name=event_name, invalid_id=invalid_id):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = invalid_id
                    with self.assertRaises(ValueError):
                        safe_event(event_name, attributes)

    def test_every_closed_enum_accepts_all_documented_members(self):
        enum_cases = (
            ("page_viewed", "device_category", ("desktop", "mobile", "tablet", "unknown")),
            ("page_viewed", "referrer_category", ("direct", "search", "social", "referral", "unknown")),
            ("analysis_started", "file_type", ("pdf", "docx", "txt")),
            ("analysis_started", "file_size_bucket", ("lt_100kb", "100kb_1mb", "1mb_5mb")),
            ("analysis_started", "jd_length_bucket", ("50_199", "200_499", "500_1999", "2000_20000")),
            ("analysis_started", "algorithm_version", (ALGORITHM_VERSION,)),
            ("evidence_viewed", "resume_status", ("evidenced", "uncertain", "not_found")),
            ("draft_exported", "format", ("markdown",)),
            ("feedback_submitted", "rating", ("helpful", "neutral", "unhelpful")),
            ("suggestion_rejected", "reason_code", ("not_relevant", "not_accurate", "clarity", "usability", "other", "no_reason")),
            (
                "analysis_failed",
                "error_code",
                (
                    "JD_TOO_SHORT",
                    "JD_TOO_LONG",
                    "FILE_TOO_LARGE",
                    "UNSUPPORTED_FILE_TYPE",
                    "FILE_MIME_MISMATCH",
                    "FILE_SIGNATURE_MISMATCH",
                    "PDF_TOO_MANY_PAGES",
                    "DOCX_UNCOMPRESSED_TOO_LARGE",
                    "DOCX_COMPRESSION_RATIO_TOO_HIGH",
                    "RESUME_TEXT_EMPTY",
                    "ANALYSIS_BUSY",
                    "ANALYSIS_TIMEOUT",
                    "EVENT_TOO_LARGE",
                    "INVALID_EVENT",
                ),
            ),
        )
        for event_name, field_name, values in enum_cases:
            for value in values:
                with self.subTest(event_name=event_name, field_name=field_name, value=value):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = value
                    self.assertEqual(
                        safe_event(event_name, attributes)["attributes"][field_name],
                        value,
                    )

    def test_every_categorical_field_rejects_values_outside_its_enum(self):
        cases = (
            ("page_viewed", "device_category"),
            ("page_viewed", "referrer_category"),
            ("analysis_started", "file_type"),
            ("analysis_started", "file_size_bucket"),
            ("analysis_started", "jd_length_bucket"),
            ("analysis_started", "algorithm_version"),
            ("upload_validation_failed", "error_code"),
            ("evidence_viewed", "resume_status"),
            ("suggestion_accepted", "algorithm_version"),
            ("suggestion_rejected", "reason_code"),
            ("draft_exported", "format"),
            ("feedback_submitted", "rating"),
            ("feedback_submitted", "reason_code"),
        )
        for event_name, field_name in cases:
            with self.subTest(event_name=event_name, field_name=field_name):
                attributes = dict(VALID_EVENTS[event_name])
                attributes[field_name] = "not_allowed"
                with self.assertRaises(ValueError):
                    safe_event(event_name, attributes)

    def test_numeric_fields_require_nonnegative_finite_nonboolean_numbers(self):
        numeric_fields = (
            ("analysis_succeeded", "processing_ms"),
            ("analysis_succeeded", "known_count"),
            ("analysis_succeeded", "unknown_count"),
            ("analysis_succeeded", "evidenced_count"),
            ("analysis_succeeded", "uncertain_count"),
            ("analysis_failed", "processing_ms"),
            ("draft_exported", "suggestion_count"),
            ("draft_exported", "pending_count"),
        )
        for event_name, field_name in numeric_fields:
            for valid_value in (0, 1, 1.5):
                with self.subTest(event_name=event_name, field_name=field_name, valid=valid_value):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = valid_value
                    self.assertEqual(
                        safe_event(event_name, attributes)["attributes"][field_name],
                        valid_value,
                    )
            for invalid_value in (-1, math.inf, -math.inf, math.nan, True, "1"):
                with self.subTest(event_name=event_name, field_name=field_name, invalid=invalid_value):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = invalid_value
                    with self.assertRaises(ValueError):
                        safe_event(event_name, attributes)

    def test_boolean_fields_require_actual_booleans(self):
        for event_name, field_name in (
            ("analysis_failed", "retryable"),
            ("suggestion_edited", "confirmed_pending_facts"),
        ):
            for valid_value in (True, False):
                attributes = dict(VALID_EVENTS[event_name])
                attributes[field_name] = valid_value
                self.assertIs(
                    safe_event(event_name, attributes)["attributes"][field_name],
                    valid_value,
                )
            for invalid_value in (0, 1, "true", None):
                with self.subTest(event_name=event_name, field_name=field_name, invalid=invalid_value):
                    attributes = dict(VALID_EVENTS[event_name])
                    attributes[field_name] = invalid_value
                    with self.assertRaises(ValueError):
                        safe_event(event_name, attributes)

    def test_pii_newline_url_phone_and_oversized_strings_reject_the_whole_event(self):
        private_values = (
            "email-me@example.com",
            "+61 412 345 678",
            "https://example.com/private",
            "line-one\nline-two",
            "x" * 65,
        )
        for private_value in private_values:
            with self.subTest(private_value=private_value):
                with self.assertRaises(ValueError):
                    safe_event("suggestion_rejected", {
                        **VALID_EVENTS["suggestion_rejected"],
                        "reason_code": private_value,
                    })
                with self.assertRaises(ValueError):
                    safe_event("analysis_succeeded", {
                        **VALID_EVENTS["analysis_succeeded"],
                        "resume_text": private_value,
                    })


class TelemetryEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(serve_static=False), raise_server_exceptions=False)

    def _post_event(self, name="analysis_succeeded", attributes=None, **kwargs):
        return self.client.post(
            "/api/v1/events",
            json={"name": name, "attributes": attributes or VALID_EVENTS[name]},
            **kwargs,
        )

    def test_valid_event_logs_one_sanitized_json_line_and_returns_204(self):
        attributes = {
            **VALID_EVENTS["analysis_succeeded"],
            "resume_text": "private",
            "filename": "Jane-Doe-resume.txt",
        }
        with log_messages("api.telemetry") as messages:
            response = self._post_event(attributes=attributes)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertRegex(response.headers["x-request-id"], r"^[a-f0-9]{32}$")
        info_events = [json.loads(message) for message in messages if '"analysis_succeeded"' in message]
        self.assertEqual(info_events, [{
            "name": "analysis_succeeded",
            "attributes": VALID_EVENTS["analysis_succeeded"],
        }])
        logged = "\n".join(messages)
        self.assertNotIn("resume_text", logged)
        self.assertNotIn("Jane-Doe", logged)

    def test_event_body_limit_is_inclusive_and_checked_before_json_parsing(self):
        body = json.dumps({
            "name": "page_viewed",
            "attributes": VALID_EVENTS["page_viewed"],
        }).encode("utf-8")
        exact_limit_body = body + b" " * (4096 - len(body))
        accepted = self.client.post(
            "/api/v1/events",
            content=exact_limit_body,
            headers={"content-type": "application/json"},
        )
        self.assertEqual(accepted.status_code, 204)

        private_tail = b"private-resume@example.com" + b"x" * 4097
        with log_messages("api.telemetry") as messages:
            rejected = self.client.post(
                "/api/v1/events",
                content=private_tail,
                headers={"content-type": "application/json"},
            )
        self.assertEqual(rejected.status_code, 413)
        self.assertEqual(rejected.json()["error_code"], "EVENT_TOO_LARGE")
        self.assertEqual(rejected.json()["request_id"], rejected.headers["x-request-id"])
        self.assertNotIn("private-resume@example.com", "\n".join(messages))

    def test_endpoint_accepts_only_name_and_attributes_top_level_fields(self):
        invalid_bodies = (
            {},
            [],
            {"name": "page_viewed"},
            {"attributes": {}},
            {"name": "page_viewed", "attributes": {}, "resume_text": "private"},
            {"name": "page_viewed", "attributes": []},
        )
        for body in invalid_bodies:
            with self.subTest(body=body):
                response = self.client.post("/api/v1/events", json=body)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error_code"], "INVALID_EVENT")

    def test_malformed_json_and_schema_rejections_never_echo_or_log_raw_input(self):
        raw_inputs = (
            b'{"name":"page_viewed","attributes":{"device_category":"email@example.com"}}',
            b'{"name":"page_viewed","attributes":',
            b"\xff\xfeprivate@example.com",
        )
        for raw in raw_inputs:
            with self.subTest(raw=raw), log_messages("api.telemetry") as messages:
                response = self.client.post(
                    "/api/v1/events",
                    content=raw,
                    headers={"content-type": "application/json"},
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error_code"], "INVALID_EVENT")
                combined = response.text + "\n" + "\n".join(messages)
                self.assertNotIn("private@example.com", combined)
                self.assertNotIn("email@example.com", combined)


class AnalysisTelemetryTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app(serve_static=False), raise_server_exceptions=False)
        self.jd = "We require Python and RAG experience in deployed projects. " * 2
        self.resume_body = "PRIVATE RESUME: built and deployed a Python service."
        self.filename = "Jane-Doe-private-resume.txt"

    def _post_analysis(self, *, content_type="text/plain"):
        return self.client.post(
            "/api/v1/analyses",
            data={
                "jd": self.jd,
                "role": "ai_agent",
                "privacy_consent_version": "2026-08-11",
            },
            files={
                "resume": (
                    self.filename,
                    self.resume_body,
                    content_type,
                ),
            },
        )

    def _event_entries(self, messages):
        return [
            json.loads(message)
            for message in messages
            if json.loads(message).get("name")
        ]

    def test_analysis_start_and_success_share_returned_opaque_id_and_safe_aggregates(self):
        with log_messages("api.telemetry") as messages:
            response = self._post_analysis()

        self.assertEqual(response.status_code, 200)
        analysis_id = response.json()["analysis_id"]
        events = self._event_entries(messages)
        self.assertEqual([event["name"] for event in events], [
            "analysis_started",
            "analysis_succeeded",
        ])
        self.assertEqual(events[0], {
            "name": "analysis_started",
            "attributes": {
                "analysis_id": analysis_id,
                "file_type": "txt",
                "file_size_bucket": "lt_100kb",
                "jd_length_bucket": "50_199",
                "algorithm_version": ALGORITHM_VERSION,
            },
        })
        success = events[1]["attributes"]
        self.assertEqual(success["analysis_id"], analysis_id)
        self.assertEqual(success["file_type"], "txt")
        self.assertEqual(success["algorithm_version"], ALGORITHM_VERSION)
        self.assertGreaterEqual(success["processing_ms"], 0)
        summary = response.json()["coverage_summary"]
        self.assertEqual(success["known_count"], summary["known_requirement_count"])
        self.assertEqual(success["unknown_count"], summary["unknown_requirement_count"])
        self.assertEqual(success["evidenced_count"], summary["evidenced_count"])
        self.assertEqual(success["uncertain_count"], summary["uncertain_count"])

        logged = "\n".join(messages)
        self.assertNotIn(self.jd, logged)
        self.assertNotIn(self.resume_body, logged)
        self.assertNotIn(self.filename, logged)
        self.assertNotIn("Jane-Doe", logged)

    def test_upload_failure_uses_one_analysis_id_and_never_logs_raw_inputs(self):
        with log_messages("api.telemetry") as messages:
            response = self._post_analysis(content_type="application/pdf")

        self.assertEqual(response.status_code, 415)
        events = self._event_entries(messages)
        self.assertEqual([event["name"] for event in events], [
            "analysis_started",
            "upload_validation_failed",
            "analysis_failed",
        ])
        analysis_ids = {
            event["attributes"]["analysis_id"]
            for event in events
        }
        self.assertEqual(len(analysis_ids), 1)
        analysis_id = analysis_ids.pop()
        self.assertRegex(analysis_id, r"^[a-f0-9]{32}$")
        self.assertEqual(
            events[1]["attributes"],
            {
                "analysis_id": analysis_id,
                "error_code": "FILE_MIME_MISMATCH",
                "file_type": "txt",
                "file_size_bucket": "lt_100kb",
            },
        )
        self.assertEqual(events[2]["attributes"]["analysis_id"], analysis_id)
        self.assertEqual(events[2]["attributes"]["error_code"], "FILE_MIME_MISMATCH")
        self.assertGreaterEqual(events[2]["attributes"]["processing_ms"], 0)
        self.assertFalse(events[2]["attributes"]["retryable"])

        logged = "\n".join(messages)
        self.assertNotIn(self.jd, logged)
        self.assertNotIn(self.resume_body, logged)
        self.assertNotIn(self.filename, logged)
        self.assertNotIn("Jane-Doe", logged)


class RequestBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(serve_static=False)
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def _post_success_input(self, headers=None):
        return self.client.post(
            "/api/v1/analyses",
            headers=headers,
            data={
                "jd": "We require Python and RAG experience in deployed projects. " * 2,
                "role": "ai_agent",
                "privacy_consent_version": "2026-08-11",
            },
            files={
                "resume": (
                    "Jane-Doe-resume.txt",
                    "Private resume body: built a Python service.",
                    "text/plain",
                ),
            },
        )

    def assert_security_headers(self, response):
        for key, value in SECURITY_HEADERS.items():
            self.assertEqual(response.headers.get(key), value)

    def test_safe_incoming_request_id_is_reused_in_success_header_only(self):
        response = self._post_success_input(headers={"x-request-id": "Beta_123-ABC"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["x-request-id"], "Beta_123-ABC")
        self.assertNotIn("request_id", response.json())
        self.assert_security_headers(response)

    def test_unsafe_incoming_request_ids_are_replaced_with_uuid_hex(self):
        for supplied in ("bad id", "bad.dot", "bad:colon", "bad/slash", "x" * 65):
            with self.subTest(supplied=supplied):
                response = self.client.get("/api/health", headers={"x-request-id": supplied})
                generated = response.headers["x-request-id"]
                self.assertRegex(generated, r"^[a-f0-9]{32}$")
                self.assertNotEqual(generated, supplied)

    def test_api_error_and_validation_error_share_safe_structured_contract(self):
        api_error = self.client.post(
            "/api/v1/analyses",
            headers={"x-request-id": "api-error-1"},
            data={"jd": "too short", "privacy_consent_version": "2026-08-11"},
        )
        validation_sentinel = "RAW-RESUME-private@example.com"
        validation_error = self.client.post(
            "/api/v1/analyses",
            headers={"x-request-id": "validation-error-1"},
            data={
                "jd": "We require Python experience in deployed projects. " * 2,
                "privacy_consent_version": "2026-08-11",
            },
            files={"resume": (None, validation_sentinel)},
        )

        for response, status, code, request_id in (
            (api_error, 400, "JD_TOO_SHORT", "api-error-1"),
            (validation_error, 422, "REQUEST_VALIDATION_FAILED", "validation-error-1"),
        ):
            with self.subTest(code=code):
                self.assertEqual(response.status_code, status)
                self.assertEqual(
                    set(response.json()),
                    {"ok", "error_code", "message", "request_id", "retryable", "supported_action"},
                )
                self.assertEqual(response.json()["error_code"], code)
                self.assertEqual(response.json()["request_id"], request_id)
                self.assertEqual(response.headers["x-request-id"], request_id)
                self.assertNotIn(validation_sentinel, response.text)
                self.assert_security_headers(response)

    def test_generic_exception_is_contained_and_logs_only_safe_metadata(self):
        private_exception = "RAW JD and resume: private@example.com +61 412 345 678"

        @self.app.get("/_test/generic-error", name="generic_failure_test_route")
        def generic_failure():
            raise RuntimeError(private_exception)

        with log_messages("api.errors") as messages:
            response = self.client.get(
                "/_test/generic-error",
                headers={"x-request-id": "generic-error-1"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {
            "ok": False,
            "error_code": "INTERNAL_ERROR",
            "message": "服务暂时无法完成请求，请稍后重试。",
            "request_id": "generic-error-1",
            "retryable": True,
            "supported_action": "请稍后重试；若问题持续，请提供请求编号。",
        })
        self.assertEqual(response.headers["x-request-id"], "generic-error-1")
        self.assert_security_headers(response)
        self.assertEqual(len(messages), 1)
        entry = json.loads(messages[0])
        self.assertEqual(
            set(entry),
            {"exception_class", "request_id", "route", "duration_ms"},
        )
        self.assertEqual(entry["exception_class"], "RuntimeError")
        self.assertEqual(entry["request_id"], "generic-error-1")
        self.assertEqual(entry["route"], "generic_failure_test_route")
        self.assertGreaterEqual(entry["duration_ms"], 0)
        self.assertNotIn(private_exception, "\n".join(messages))
        self.assertNotIn("private@example.com", response.text)

    def test_request_and_security_headers_cover_health_404_and_event_errors(self):
        responses = (
            self.client.get("/api/health"),
            self.client.get("/does-not-exist"),
            self.client.post(
                "/api/v1/events",
                content=b"x" * 4097,
                headers={"content-type": "application/json"},
            ),
        )
        for response in responses:
            with self.subTest(status=response.status_code):
                self.assertRegex(response.headers["x-request-id"], r"^[a-f0-9]{32}$")
                self.assert_security_headers(response)

    def test_cors_allows_only_configured_origins_and_never_wildcard(self):
        for origin in ALLOWED_ORIGINS:
            with self.subTest(origin=origin):
                response = self.client.options(
                    "/api/v1/events",
                    headers={
                        "origin": origin,
                        "access-control-request-method": "POST",
                        "access-control-request-headers": "content-type,x-request-id",
                    },
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.headers.get("access-control-allow-origin"), origin)
                self.assertNotEqual(response.headers.get("access-control-allow-origin"), "*")
                self.assert_security_headers(response)

        rejected = self.client.options(
            "/api/v1/events",
            headers={
                "origin": "https://evil.example",
                "access-control-request-method": "POST",
            },
        )
        self.assertEqual(rejected.status_code, 400)
        self.assertIsNone(rejected.headers.get("access-control-allow-origin"))
        self.assert_security_headers(rejected)

    def test_vercel_headers_exactly_match_local_security_contract(self):
        config = json.loads(Path("vercel.json").read_text(encoding="utf-8"))
        self.assertEqual(
            config,
            {
                "$schema": "https://openapi.vercel.sh/vercel.json",
                "headers": [
                    {
                        "source": "/(.*)",
                        "headers": [
                            {"key": "X-Content-Type-Options", "value": SECURITY_HEADERS["x-content-type-options"]},
                            {"key": "Referrer-Policy", "value": SECURITY_HEADERS["referrer-policy"]},
                            {"key": "Permissions-Policy", "value": SECURITY_HEADERS["permissions-policy"]},
                            {"key": "Content-Security-Policy", "value": SECURITY_HEADERS["content-security-policy"]},
                        ],
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
