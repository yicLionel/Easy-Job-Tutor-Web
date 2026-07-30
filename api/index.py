# -*- coding: utf-8 -*-
"""Vercel Serverless 函数入口：把 FastAPI 应用包装为 ASGI handler。

Vercel 会把 /api/* 请求路由到这里，由 Mangum 转发给 FastAPI 处理。
后端业务代码在 backend/ 目录，这里仅做路径挂载与适配。
"""
import os
import sys

# 让 backend/ 下的模块可被导入
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Vercel 上不通过 FastAPI 托管静态文件（由 Vercel 直接托管根目录静态资源）
os.environ["SERVE_STATIC"] = "0"

from main import create_app  # noqa: E402

try:
    from mangum import Mangum  # noqa: E402

    handler = Mangum(create_app())
except Exception:  # pragma: no cover - 兜底，正常不应触发
    app = create_app()
