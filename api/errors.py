"""Structured, privacy-safe API error and request-boundary helpers."""

from dataclasses import dataclass
import json
import logging
from math import isfinite
from time import perf_counter
import re
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
        "base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    ),
}


@dataclass
class ApiError(Exception):
    status_code: int
    error_code: str
    message: str
    retryable: bool = False
    supported_action: str = ""

    def __str__(self) -> str:
        return self.message


def safe_request_id(value: str | None) -> str:
    """Reuse a syntactically safe caller ID or generate an opaque UUID hex ID."""
    if isinstance(value, str) and REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return uuid.uuid4().hex


def request_id_for(request: Request) -> str:
    request_id = getattr(request.state, "request_id", None)
    if not isinstance(request_id, str):
        request_id = safe_request_id(request.headers.get("x-request-id"))
        request.state.request_id = request_id
    return request_id


def apply_boundary_headers(response, request_id: str) -> None:
    response.headers["X-Request-ID"] = request_id
    for key, value in SECURITY_HEADERS.items():
        response.headers[key] = value


def structured_error_response(
    request: Request,
    *,
    status_code: int,
    error_code: str,
    message: str,
    retryable: bool = False,
    supported_action: str = "",
) -> JSONResponse:
    request_id = request_id_for(request)
    response = JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error_code": error_code,
            "message": message,
            "request_id": request_id,
            "retryable": retryable,
            "supported_action": supported_action,
        },
    )
    apply_boundary_headers(response, request_id)
    return response


def api_error_response(request: Request, exc: ApiError) -> JSONResponse:
    return structured_error_response(
        request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        retryable=exc.retryable,
        supported_action=exc.supported_action,
    )


def validation_error_response(request: Request) -> JSONResponse:
    return structured_error_response(
        request,
        status_code=422,
        error_code="REQUEST_VALIDATION_FAILED",
        message="请求字段格式不正确。",
        supported_action="请检查提交字段和文件后重试。",
    )


def _request_duration_ms(request: Request) -> float:
    started_at = getattr(request.state, "request_started_at", perf_counter())
    duration_ms = max(0.0, (perf_counter() - started_at) * 1000)
    return round(duration_ms if isfinite(duration_ms) else 0.0, 3)


def _route_name(request: Request) -> str:
    route = request.scope.get("route")
    name = getattr(route, "name", None)
    if not isinstance(name, str):
        endpoint = request.scope.get("endpoint")
        name = getattr(endpoint, "__name__", None)
    if isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", name):
        return name
    return "unmatched"


def generic_error_response(request: Request, exc: Exception) -> JSONResponse:
    request_id = request_id_for(request)
    if not getattr(request.state, "generic_error_logged", False):
        exception_class = type(exc).__name__
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,63}", exception_class):
            exception_class = "Exception"
        entry = {
            "exception_class": exception_class,
            "request_id": request_id,
            "route": _route_name(request),
            "duration_ms": _request_duration_ms(request),
        }
        logger.error(json.dumps(entry, separators=(",", ":"), sort_keys=True))
        request.state.generic_error_logged = True
    return structured_error_response(
        request,
        status_code=500,
        error_code="INTERNAL_ERROR",
        message="服务暂时无法完成请求，请稍后重试。",
        retryable=True,
        supported_action="请稍后重试；若问题持续，请提供请求编号。",
    )
