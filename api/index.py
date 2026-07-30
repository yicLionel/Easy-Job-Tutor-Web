# -*- coding: utf-8 -*-
"""Vercel Serverless 函数入口：把 FastAPI 应用包装为 ASGI handler。

Vercel 会把 /api/* 请求路由到这里，由 Mangum 转发给 FastAPI 处理。
后端业务代码与入口同目录（api/），由 Vercel 自动打包，无需 includeFiles。
"""
import os

# Vercel 上不通过 FastAPI 托管静态文件（由 Vercel 直接托管根目录静态资源）
os.environ["SERVE_STATIC"] = "0"

from main import create_app  # noqa: E402

try:
    from mangum import Mangum  # noqa: E402

    handler = Mangum(create_app())
except Exception:  # pragma: no cover - 兜底，正常不应触发
    app = create_app()
