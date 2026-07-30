# -*- coding: utf-8 -*-
"""Vercel ASGI 函数入口。

Vercel 的 Python 运行时会自动识别模块顶层的 ASGI 应用实例（`app` 变量），
并将其包装为 Serverless 函数。不需要任何适配器。

注意：Vercel 只把 api/index.py 映射到 /api（精确路径），不自动路由子路径。
`vercel.json` 中需配置 rewrites 来映射 /api/* → /api 函数。
"""
import os

os.environ["SERVE_STATIC"] = "0"

from main import create_app

app = create_app()
