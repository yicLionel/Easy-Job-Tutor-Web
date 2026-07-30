# -*- coding: utf-8 -*-
"""Vercel ASGI 函数入口（带错误兜底，便于调试）。

Vercel 的 Python 运行时原生支持 ASGI 应用——只要模块顶层有 `app` 变量指向
ASGI 实例，Vercel 会自动识别并包装成 Serverless 函数。

注意：Vercel 只把 api/index.py 映射到 /api（精确路径），不自动路由子路径。
`vercel.json` 中需配置 rewrites 来映射 /api/* → /api 函数。
"""
import os
import traceback

os.environ["SERVE_STATIC"] = "0"

from main import create_app

_fastapi_app = create_app()


async def app(scope, receive, send):
    """在 FastAPI 外层包一个 try/except，让调试信息能暴露出来。"""
    try:
        await _fastapi_app(scope, receive, send)
    except Exception:
        tb = traceback.format_exc()
        body = tb.encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [[b"content-type", b"text/plain; charset=utf-8"]],
        })
        await send({"type": "http.response.body", "body": body})
