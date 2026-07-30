# -*- coding: utf-8 -*-
"""Vercel ASGI 函数入口。

Vercel 的 Python 运行时原生支持 ASGI 应用——只要把 FastAPI 实例��出为 `app`
变量，Vercel 会自动识别并包装成 Serverless 函数。不需要 Mangum，
不需要 `vercel` 包，不需要自定义 handler。

注意：Vercel 会把 /api 目录下的文件按文件系统路由映射。
api/index.py → handled by app, request path 保留完整前缀 /api/*。
"""
import os

# Vercel 上不通过 FastAPI 托管前端静态文件（由 Vercel 直接托管）
os.environ["SERVE_STATIC"] = "0"

from main import create_app

app = create_app()
