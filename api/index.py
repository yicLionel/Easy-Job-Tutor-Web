# -*- coding: utf-8 -*-
"""Vercel Serverless 函数入口（原生 handler，不依赖 Mangum）。

Vercel 的 Python 运行时只认自己的 Request/Response 格式，Mangum 是给 AWS Lambda
用的、不兼容 Vercel，所以不能用来包 FastAPI。这里直接用 Vercel 原生 handler，
自行用标准库解析 multipart 上传的简历，调用后端纯逻辑模块（parser/matcher/learning）。

后端业务代码与入口同目录（api/），由 Vercel 自动打包。
本地开发仍用 backend/main.py 的 FastAPI（uvicorn api.main:app），互不影响。
"""
import os
import sys
import json
import email
from email import policy

# 确保 api/ 在模块搜索路径中，使 `from parser import ...` 可解析
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from vercel import Request, Response  # Vercel Python 运行时内置
except ImportError:
    Request = Response = None  # 非 Vercel 环境（本地测试）下占位，不影响运行

from parser import parse_resume
from matcher import analyze
from learning import build_path, build_interview


def _norm_headers(request):
    hdrs = getattr(request, "headers", None) or {}
    if not isinstance(hdrs, dict):
        try:
            hdrs = dict(hdrs)
        except Exception:
            hdrs = {}
    return {str(k).lower(): v for k, v in hdrs.items()}


def _request_body(request):
    body = getattr(request, "body", None)
    if body is None and hasattr(request, "get_data"):
        try:
            body = request.get_data()
        except Exception:
            body = None
    if isinstance(body, str):
        body = body.encode("utf-8")
    return body or b""


def _request_path(request):
    p = getattr(request, "path", None)
    if p:
        return p
    url = getattr(request, "url", "") or ""
    return url.split("?", 1)[0]


def parse_form(body: bytes, content_type: str):
    """解析 multipart/form-data 或 application/x-www-form-urlencoded，返回字段字典。

    文件字段的值为 {"filename": str, "data": bytes}；普通字段为 str。
    """
    ctype = (content_type or "").lower()
    if ctype.startswith("multipart/form-data"):
        raw = ("Content-Type: " + content_type + "\r\n\r\n").encode() + body
        msg = email.message_from_bytes(raw, policy=policy.default)
        fields = {}
        for part in msg.walk():
            disp = part.get("Content-Disposition", "")
            if not disp:
                continue
            name = filename = None
            for tok in disp.split(";"):
                tok = tok.strip()
                if tok.startswith("name="):
                    name = tok[5:].strip('"').strip("'")
                elif tok.startswith("filename="):
                    filename = tok[9:].strip('"').strip("'")
            if not name:
                continue
            payload = part.get_payload(decode=True) or b""
            if filename:
                fields[name] = {"filename": filename, "data": payload}
            else:
                fields[name] = payload.decode("utf-8", "ignore") if payload else ""
        return fields
    # urlencoded
    from urllib.parse import parse_qs
    parsed = parse_qs(body.decode("utf-8", "ignore"))
    return {k: (v[0] if v else "") for k, v in parsed.items()}


def _json(body, status=200):
    return Response(
        json.dumps(body, ensure_ascii=False),
        status=status,
        headers={"Content-Type": "application/json; charset=utf-8"},
    )


def _get_fields(request):
    """获取表单字段。优先用 Vercel 官方 request.form()，失败则回退解析原始 body。

    文件字段统一规整为 {"filename": str, "data": bytes}；普通字段为 str。
    """
    form = getattr(request, "form", None)
    if callable(form):
        try:
            res = form()
            if hasattr(res, "__await__"):
                import asyncio
                loop = asyncio.new_event_loop()
                try:
                    res = loop.run_until_complete(res)
                finally:
                    loop.close()
            if isinstance(res, dict):
                out = {}
                for k, v in res.items():
                    if hasattr(v, "filename") and hasattr(v, "read"):
                        data = v.read()
                        if isinstance(data, str):
                            data = data.encode("utf-8")
                        out[k] = {"filename": v.filename or "resume", "data": data or b""}
                    else:
                        out[k] = v.decode("utf-8", "ignore") if isinstance(v, bytes) else str(v)
                return out
        except Exception:
            pass
    body = _request_body(request)
    headers = _norm_headers(request)
    return parse_form(body, headers.get("content-type", ""))


def _analyze(request: Request) -> Response:
    fields = _get_fields(request)

    jd = fields.get("jd", "")
    if isinstance(jd, dict):
        jd = ""
    role = fields.get("role", "auto")
    if isinstance(role, dict):
        role = "auto"
    resume_field = fields.get("resume")

    if not isinstance(resume_field, dict) or not resume_field.get("data"):
        return _json({"ok": False, "error": "缺少简历文件（请上传 PDF / Word / TXT）。"}, status=400)

    filename = resume_field.get("filename") or "resume.pdf"
    raw = resume_field.get("data") or b""
    resume_text = parse_resume(filename, raw)

    if not resume_text.strip():
        return _json({
            "ok": False,
            "error": "未能从简历中提取到文字内容，请确认文件为可复制文本的 PDF / Word（扫描件图片暂不支持）。",
        })

    match = analyze(jd_text=jd, resume_text=resume_text, role=role)
    match["ok"] = True
    match["resume_length"] = len(resume_text)
    match["learning_path"] = build_path(match["role"], match["gaps"])
    match["interview"] = build_interview(match["role"], match["gaps"])
    return _json(match)


def handler(request: Request) -> Response:
    method = (getattr(request, "method", "GET") or "GET").upper()
    path = _request_path(request).rstrip("/")

    if method == "GET" and (path.endswith("/health") or path == "/api"):
        return _json({"status": "ok"})

    if method == "POST" and path.endswith("/analyze"):
        return _analyze(request)

    return _json({"detail": "Not Found"}, status=404)
