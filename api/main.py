# -*- coding: utf-8 -*-
"""FastAPI entrypoint for the versioned public-Beta analysis contract."""
import json
import os
from pathlib import Path
import secrets
from time import perf_counter
from typing import Optional

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from api.config import ALGORITHM_VERSION, ALLOWED_ORIGINS, PRIVACY_CONSENT_VERSION
from api.errors import (
    ApiError,
    api_error_response,
    apply_boundary_headers,
    generic_error_response,
    safe_request_id,
    validation_error_response,
)
from api.matcher import analyze_public_beta
from api.parser import parse_validated_resume
from api.telemetry import (
    TelemetryValidationError,
    log_event,
    log_rejection,
    safe_event,
)
from api.validation import validate_jd, validate_upload


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MAX_EVENT_BODY_BYTES = 4 * 1024


def _file_type(filename: str) -> str | None:
    suffix = Path(filename or "").suffix.lower().removeprefix(".")
    return suffix if suffix in {"pdf", "docx", "txt"} else None


def _file_size_bucket(size_bytes: int) -> str | None:
    if size_bytes < 100 * 1024:
        return "lt_100kb"
    if size_bytes < 1024 * 1024:
        return "100kb_1mb"
    if size_bytes <= 5 * 1024 * 1024:
        return "1mb_5mb"
    return None


def _jd_length_bucket(length: int) -> str:
    if length <= 199:
        return "50_199"
    if length <= 499:
        return "200_499"
    if length <= 1999:
        return "500_1999"
    return "2000_20000"


def _processing_ms(started_at: float) -> float:
    return round(max(0.0, (perf_counter() - started_at) * 1000), 3)


def create_app(serve_static: bool | None = None) -> FastAPI:
    app = FastAPI(title="AI 简历优化与面试辅导", version="0.3.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ALLOWED_ORIGINS),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def apply_request_boundary(request: Request, call_next):
        request.state.request_started_at = perf_counter()
        request.state.request_id = safe_request_id(request.headers.get("x-request-id"))
        try:
            response = await call_next(request)
        except ApiError as exc:
            response = api_error_response(request, exc)
        except RequestValidationError:
            response = validation_error_response(request)
        except Exception as exc:
            response = generic_error_response(request, exc)
        if request.url.path == "/api/analyze":
            response.headers["Deprecation"] = "true"
        apply_boundary_headers(response, request.state.request_id)
        return response

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        return api_error_response(request, exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ):
        return validation_error_response(request)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return generic_error_response(request, exc)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    async def read_event_body(request: Request) -> bytes:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_EVENT_BODY_BYTES:
                    log_rejection("event_too_large")
                    raise ApiError(
                        413,
                        "EVENT_TOO_LARGE",
                        "遥测事件不能超过 4 KiB。",
                    )
            except ValueError:
                log_rejection("invalid_event")
                raise ApiError(400, "INVALID_EVENT", "遥测事件格式不正确。")

        body = bytearray()
        async for chunk in request.stream():
            remaining = MAX_EVENT_BODY_BYTES + 1 - len(body)
            body.extend(chunk[:remaining])
            if len(body) > MAX_EVENT_BODY_BYTES or len(chunk) > remaining:
                log_rejection("event_too_large")
                raise ApiError(
                    413,
                    "EVENT_TOO_LARGE",
                    "遥测事件不能超过 4 KiB。",
                )
        return bytes(body)

    @app.post("/api/v1/events", status_code=204)
    async def telemetry_endpoint(request: Request):
        raw = await read_event_body(request)
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            log_rejection("invalid_event")
            raise ApiError(400, "INVALID_EVENT", "遥测事件格式不正确。")

        if not isinstance(payload, dict) or set(payload) != {"name", "attributes"}:
            log_rejection("invalid_event")
            raise ApiError(400, "INVALID_EVENT", "遥测事件格式不正确。")
        try:
            event = safe_event(payload["name"], payload["attributes"])
        except TelemetryValidationError as exc:
            log_rejection(exc.reason_code)
            raise ApiError(400, "INVALID_EVENT", "遥测事件格式不正确。")
        log_event(event)
        return Response(status_code=204)

    async def handle_analysis(
        jd: Optional[str],
        role: str,
        resume: Optional[UploadFile],
        privacy_consent_version: Optional[str],
    ) -> dict:
        analysis_started_at = perf_counter()
        if privacy_consent_version != PRIVACY_CONSENT_VERSION:
            raise ApiError(
                400,
                "PRIVACY_CONSENT_REQUIRED",
                "请确认当前版本的隐私说明后再提交。",
                supported_action="请重新勾选隐私同意选项。",
            )
        validated_jd = validate_jd(jd)
        if resume is None or not resume.filename:
            raise ApiError(
                400,
                "RESUME_REQUIRED",
                "请上传简历文件。",
                supported_action="请上传 PDF、DOCX 或 TXT 简历。",
            )

        raw = await resume.read()
        analysis_id = secrets.token_hex(16)
        file_type = _file_type(resume.filename)
        file_size_bucket = _file_size_bucket(len(raw))
        started_attributes = {
            "analysis_id": analysis_id,
            "jd_length_bucket": _jd_length_bucket(len(validated_jd)),
            "algorithm_version": ALGORITHM_VERSION,
        }
        if file_type:
            started_attributes["file_type"] = file_type
        if file_size_bucket:
            started_attributes["file_size_bucket"] = file_size_bucket
        log_event(safe_event("analysis_started", started_attributes))

        try:
            upload = validate_upload(
                resume.filename,
                resume.content_type,
                raw,
            )
            resume_text = parse_validated_resume(upload)
            result = analyze_public_beta(
                validated_jd,
                resume_text,
                analysis_id,
                role=role,
            )
        except ApiError as exc:
            failure_attributes = {
                "analysis_id": analysis_id,
                "error_code": exc.error_code,
                "processing_ms": _processing_ms(analysis_started_at),
                "retryable": exc.retryable,
            }
            upload_failure_attributes = {
                "analysis_id": analysis_id,
                "error_code": exc.error_code,
            }
            if file_type:
                upload_failure_attributes["file_type"] = file_type
            if file_size_bucket:
                upload_failure_attributes["file_size_bucket"] = file_size_bucket
            try:
                log_event(safe_event("upload_validation_failed", upload_failure_attributes))
                log_event(safe_event("analysis_failed", failure_attributes))
            except TelemetryValidationError:
                log_rejection("invalid_server_event")
            raise

        summary = result["coverage_summary"]
        log_event(
            safe_event(
                "analysis_succeeded",
                {
                    "analysis_id": analysis_id,
                    "file_type": upload.kind,
                    "processing_ms": _processing_ms(analysis_started_at),
                    "algorithm_version": ALGORITHM_VERSION,
                    "known_count": summary["known_requirement_count"],
                    "unknown_count": summary["unknown_requirement_count"],
                    "evidenced_count": summary["evidenced_count"],
                    "uncertain_count": summary["uncertain_count"],
                },
            )
        )
        return result

    @app.post("/api/v1/analyses")
    async def analyze_endpoint(
        jd: Optional[str] = Form(None),
        role: str = Form("auto"),
        resume: Optional[UploadFile] = File(None),
        privacy_consent_version: Optional[str] = Form(None),
    ):
        return await handle_analysis(
            jd,
            role,
            resume,
            privacy_consent_version,
        )

    @app.post("/api/analyze")
    async def legacy_analyze_endpoint(
        jd: Optional[str] = Form(None),
        role: str = Form("auto"),
        resume: Optional[UploadFile] = File(None),
        privacy_consent_version: Optional[str] = Form(None),
    ):
        return await handle_analysis(
            jd,
            role,
            resume,
            privacy_consent_version,
        )

    should_serve_static = (
        os.getenv("SERVE_STATIC", "1") == "1"
        if serve_static is None
        else serve_static
    )
    if should_serve_static and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
        app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

    return app


app = create_app()
