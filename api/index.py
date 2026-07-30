# -*- coding: utf-8 -*-
"""Vercel ASGI 函数入口。"""
import os

os.environ["SERVE_STATIC"] = "0"

from api.main import create_app

app = create_app()
