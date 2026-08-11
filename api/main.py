# -*- coding: utf-8 -*-
"""FastAPI entrypoint for the versioned public-Beta analysis contract."""
import os
import secrets
from typing import Optional

from fastapi import FastAPI, File, Form, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from api.config import PRIVACY_CONSENT_VERSION
from api.errors import ApiError
from api.matcher import analyze_public_beta
from api.parser import parse_validated_resume
from api.validation import validate_jd, validate_upload


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))


def create_app(serve_static: bool | None = None) -> FastAPI:
    app = FastAPI(title="AI 简历优化与面试辅导", version="0.3.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError):
        headers = (
            {"Deprecation": "true"}
            if request.url.path == "/api/analyze"
            else None
        )
        return JSONResponse(
            status_code=exc.status_code,
            headers=headers,
            content={
                "ok": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "request_id": secrets.token_hex(16),
                "retryable": exc.retryable,
                "supported_action": exc.supported_action,
            },
        )

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    async def handle_analysis(
        jd: Optional[str],
        role: str,
        resume: Optional[UploadFile],
        privacy_consent_version: Optional[str],
    ) -> dict:
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
        upload = validate_upload(
            resume.filename,
            resume.content_type,
            raw,
        )
        resume_text = parse_validated_resume(upload)
        analysis_id = secrets.token_hex(16)
        return analyze_public_beta(
            validated_jd,
            resume_text,
            analysis_id,
            role=role,
        )

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
        response: Response,
        jd: Optional[str] = Form(None),
        role: str = Form("auto"),
        resume: Optional[UploadFile] = File(None),
        privacy_consent_version: Optional[str] = Form(None),
    ):
        response.headers["Deprecation"] = "true"
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
