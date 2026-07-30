# -*- coding: utf-8 -*-
"""FastAPI 主程序：简历解析 + 匹配分析 + 学习路线 + 面试辅导。

- 本地：uvicorn main:app（同时托管根目录前端静态文件）
- Vercel：由 api/index.py 用 Mangum 包装为 Serverless 函数，静态文件由 Vercel 托管
"""
import os
import sys

# 确保 api/ 在模块搜索路径中，使 `from parser import ...` 无论从哪个目录启动都能解析
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from parser import parse_resume
from matcher import analyze
from learning import build_path, build_interview

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 前端静态文件所在目录：默认取项目根目录（api 的上一级）
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))


def create_app() -> FastAPI:
    app = FastAPI(title="AI 简历优化与面试辅导", version="0.1.0")

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
        jd: str = Form(..., description="岗位 JD 文本"),
        role: str = Form("auto", description="目标岗位：auto/ai_product/ai_agent/ai_ops"),
        resume: UploadFile = File(..., description="简历 PDF / Word / TXT"),
    ):
        raw = await resume.read()
        resume_text = parse_resume(resume.filename or "", raw)

        if not resume_text.strip():
            return {
                "ok": False,
                "error": "未能从简历中提取到文字内容，请确认文件为可复制文本的 PDF / Word（扫描件图片暂不支持）。",
            }

        match = analyze(jd_text=jd, resume_text=resume_text, role=role)
        match["ok"] = True
        match["resume_length"] = len(resume_text)

        match["learning_path"] = build_path(match["role"], match["gaps"])
        match["interview"] = build_interview(match["role"], match["gaps"])
        return match

    # 本地开发时由 FastAPI 托管前端；Vercel 上 SERVE_STATIC=0，由 Vercel 托管静态
    if os.getenv("SERVE_STATIC", "1") == "1" and os.path.isfile(os.path.join(FRONTEND_DIR, "index.html")):
        app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

    return app


app = create_app()
