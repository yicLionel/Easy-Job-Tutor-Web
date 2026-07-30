"""Vercel 入口：映射 /api/analyze。"""
import os

os.environ["SERVE_STATIC"] = "0"

from api.main import create_app

app = create_app()
