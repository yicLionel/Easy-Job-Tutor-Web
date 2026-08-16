"""Privacy-safe, closed-schema telemetry for the public Beta."""

from __future__ import annotations

import json
import logging
import math
import re
from collections.abc import Mapping
from typing import Any

from api.config import ALGORITHM_VERSION


logger = logging.getLogger(__name__)

EVENT_FIELDS = {
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

ENUM_VALUES = {
    "device_category": {"desktop", "mobile", "tablet", "unknown"},
    "referrer_category": {"direct", "search", "social", "referral", "unknown"},
    "file_type": {"pdf", "docx", "txt"},
    "file_size_bucket": {"lt_100kb", "100kb_1mb", "1mb_5mb"},
    "jd_length_bucket": {"50_199", "200_499", "500_1999", "2000_20000"},
    "algorithm_version": {ALGORITHM_VERSION},
    "error_code": {
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
    },
    "resume_status": {"evidenced", "uncertain", "not_found"},
    "reason_code": {
        "not_relevant",
        "not_accurate",
        "clarity",
        "usability",
        "other",
        "no_reason",
    },
    "format": {"markdown"},
    "rating": {"helpful", "neutral", "unhelpful"},
}

IDENTIFIER_FIELDS = {"requirement_id", "suggestion_id"}
BOOLEAN_FIELDS = {"retryable", "confirmed_pending_facts"}
NUMERIC_FIELDS = {
    "processing_ms",
    "known_count",
    "unknown_count",
    "evidenced_count",
    "uncertain_count",
    "suggestion_count",
    "pending_count",
}

_ANALYSIS_ID = re.compile(r"^[a-f0-9]{32}$")
_IDENTIFIER = re.compile(r"^[a-z0-9_-]{1,64}$")
_EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
_PHONE = re.compile(r"(?<![A-Za-z0-9])\+?(?:\d[\s().-]?){7,}\d(?![A-Za-z0-9])")
_URL = re.compile(r"(?:https?://|www\.)", re.IGNORECASE)


class TelemetryValidationError(ValueError):
    """A safe, body-free telemetry rejection with an aggregate reason."""

    def __init__(self, reason_code: str):
        super().__init__("Telemetry event rejected")
        self.reason_code = reason_code


def _reject_private_value(field_name: str, value: Any) -> None:
    if not isinstance(value, str):
        if value is None or isinstance(value, (bool, int, float)):
            return
        raise TelemetryValidationError("invalid_value")
    if len(value) > 64:
        raise TelemetryValidationError("oversized_value")
    if "\n" in value or "\r" in value:
        raise TelemetryValidationError("pii_detected")
    if _EMAIL.search(value) or _URL.search(value):
        raise TelemetryValidationError("pii_detected")
    if field_name != "analysis_id" and _PHONE.search(value):
        raise TelemetryValidationError("pii_detected")


def _validate_field(field_name: str, value: Any) -> None:
    if field_name == "analysis_id":
        if not isinstance(value, str) or not _ANALYSIS_ID.fullmatch(value):
            raise TelemetryValidationError("invalid_value")
        return
    if field_name in IDENTIFIER_FIELDS:
        if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
            raise TelemetryValidationError("invalid_value")
        return
    if field_name in ENUM_VALUES:
        if not isinstance(value, str) or value not in ENUM_VALUES[field_name]:
            raise TelemetryValidationError("invalid_value")
        return
    if field_name in BOOLEAN_FIELDS:
        if not isinstance(value, bool):
            raise TelemetryValidationError("invalid_value")
        return
    if field_name in NUMERIC_FIELDS:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise TelemetryValidationError("invalid_value")
        return
    raise TelemetryValidationError("invalid_value")


def safe_event(event_name: str, attributes: dict) -> dict:
    """Return a new event containing only validated allowlisted attributes."""
    if not isinstance(event_name, str) or event_name not in EVENT_FIELDS:
        raise TelemetryValidationError("unknown_event")
    if not isinstance(attributes, Mapping):
        raise TelemetryValidationError("invalid_attributes")
    if event_name != "page_viewed" and "analysis_id" not in attributes:
        raise TelemetryValidationError("missing_analysis_id")

    for field_name, value in attributes.items():
        _reject_private_value(str(field_name), value)

    allowed_fields = EVENT_FIELDS[event_name]
    sanitized = {}
    for field_name, value in attributes.items():
        if field_name not in allowed_fields:
            continue
        _validate_field(field_name, value)
        sanitized[field_name] = value
    return {"name": event_name, "attributes": sanitized}


def log_event(event: dict) -> None:
    """Write one compact JSON line for a previously sanitized event."""
    logger.info(json.dumps(event, ensure_ascii=True, separators=(",", ":"), sort_keys=True))


def log_rejection(reason_code: str) -> None:
    """Emit only an aggregate counter signal, never rejected event content."""
    entry = {"event": "telemetry_rejected", "reason_code": reason_code, "count": 1}
    logger.warning(json.dumps(entry, separators=(",", ":"), sort_keys=True))
