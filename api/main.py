# -*- coding: utf-8 -*-
"""FastAPI 主程序：简历解析 + 匹配分析 + 学习路线 + 面试辅导。

Gate 系统：根据输入组合自动切换分析模式。
- complete：完整材料（JD + 简历）→ 全链路分析
- jd_only：仅 JD → 岗位拆解分析
- resume_only：仅简历 → 简历基线诊断
- multi_jd：多 JD + 简历 → 多岗位对比

locale 参数支持 zh / en，切换分析结果语言。
"""
import os
import json

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from api.parser import parse_resume
from api.matcher import (
    analyze, analyze_jd_only, analyze_resume_only, multi_jd_compare,
    localize_analysis, localize_interview,
)
from api.knowledge import LABEL_EN
from api.learning import build_path, build_interview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))


def _localize_label(text: str) -> str:
    """简单本地化：用翻译表替换中文→英文。"""
    return LABEL_EN.get(text, text)


def _localize_jd_analysis(jda: dict, locale: str) -> dict:
    """本地化 JD 分析结果中的标签。"""
    if locale != "en":
        return jda
    for key in ("required_skills", "preferred_skills", "tools_technologies",
                 "domain_knowledge", "soft_skills", "core_responsibilities"):
        if key in jda:
            jda[key] = [_localize_label(s) for s in jda[key]]
    return jda


def create_app() -> FastAPI:
    app = FastAPI(title="AI 简历优化与面试辅导", version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/analyze")
    async def analyze_endpoint(
        jd: str = Form(..., description="岗位 JD 文本（仅 JD 模式也传到此字段）"),
        role: str = Form("auto", description="目标岗位：auto/ai_product/ai_agent/ai_ops"),
        resume: Optional[UploadFile] = File(None, description="简历 PDF / Word / TXT"),
        mode: str = Form("auto", description="分析模式：auto / complete / jd_only / resume_only / multi_jd"),
        jds: Optional[str] = Form(None, description="多 JD 模式：JSON 数组字符串，传入多个 JD 文本"),
        locale: str = Form("zh", description="语言：zh / en"),
    ):
        """Gate 系统主入口。根据 mode 参数和输入组合自动路由到不同分析模式。"""
        # ── Gate: 模式检测 ──────────────────────────────────
        has_resume_file = resume is not None and resume.filename is not None
        has_jd_text = bool(jd and jd.strip())
        has_multi_jd = bool(jds and jds.strip().startswith("["))

        resolved_mode = mode
        if mode == "auto":
            if has_resume_file and has_jd_text:
                resolved_mode = "complete"
            elif has_multi_jd and has_resume_file:
                resolved_mode = "multi_jd"
            elif has_jd_text and not has_resume_file:
                resolved_mode = "jd_only"
            elif has_resume_file and not has_jd_text:
                resolved_mode = "resume_only"
            else:
                return {"ok": False, "error": "请至少提供岗位 JD 文本或上传简历文件。"}

        # ── 模式路由 ────────────────────────────────────────

        # 模式 1: JD 拆解分析（仅 JD）
        if resolved_mode == "jd_only":
            jda = analyze_jd_only(jd)
            jda = _localize_jd_analysis(jda, locale)
            return {
                "ok": True,
                "mode": "jd_only",
                "jd_analysis": jda,
            }

        # 模式 2: 简历基线诊断（仅简历）
        if resolved_mode == "resume_only":
            raw = await resume.read()
            resume_text = parse_resume(resume.filename or "", raw)
            if not resume_text.strip():
                return {
                    "ok": False,
                    "error": "未能从简历中提取到文字内容，请确认文件为可复制文本的 PDF / Word（扫描件图片暂不支持）。",
                }
            diag = analyze_resume_only(resume_text)
            diag["resume_length"] = len(resume_text)
            return {"ok": True, "mode": "resume_only", "resume_diagnosis": diag}

        # 模式 3: 多 JD 对比
        if resolved_mode == "multi_jd":
            raw = await resume.read()
            resume_text = parse_resume(resume.filename or "", raw)
            if not resume_text.strip():
                return {
                    "ok": False,
                    "error": "未能从简历中提取到文字内容。",
                }
            try:
                jd_list = json.loads(jds)
            except (json.JSONDecodeError, TypeError):
                return {"ok": False, "error": "多 JD 参数格式错误，请传入 JSON 数组。"}
            if not isinstance(jd_list, list) or len(jd_list) < 2:
                return {"ok": False, "error": "多 JD 模式至少需要传入 2 个 JD 文本。"}
            comparison = multi_jd_compare(jd_list, resume_text)
            comparison["resume_length"] = len(resume_text)
            # 多 JD 对比结果本地化
            if locale == "en":
                for jd_item in comparison.get("per_jd", []):
                    jd_item["gaps"] = [
                        {**g, "label": _localize_label(g.get("label", "")),
                         "learn": "", "dim": ""}
                        for g in jd_item.get("gaps", [])
                    ]
            return {"ok": True, "mode": "multi_jd", "multi_jd_comparison": comparison}

        # ── 模式 4（默认）: 完整材料分析 ────────────────────
        raw = await resume.read()
        resume_text = parse_resume(resume.filename or "", raw)

        if not resume_text.strip():
            return {
                "ok": False,
                "error": "未能从简历中提取到文字内容，请确认文件为可复制文本的 PDF / Word（扫描件图片暂不支持）。",
            }

        match = analyze(jd_text=jd, resume_text=resume_text, role=role)
        match["ok"] = True
        match["mode"] = "complete"
        match["resume_length"] = len(resume_text)

        match["learning_path"] = build_path(match["role"], match["gaps"])
        match["interview"] = build_interview(match["role"], match["gaps"])

        # 本地化
        if locale == "en":
            match = localize_analysis(match, locale)
            match["interview"] = localize_interview(match.get("interview"), match["role"], locale)

        return match

    # 本地开发时由 FastAPI 托管前端
    if os.getenv("SERVE_STATIC", "1") == "1" and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
        app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

    return app


app = create_app()
