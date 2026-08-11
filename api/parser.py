# -*- coding: utf-8 -*-
"""简历文本抽取：支持 PDF / Word(.docx) / 纯文本(.txt)。"""
import importlib
import io
import re
import zipfile

import pdfplumber

from api.config import (
    MAX_DOCX_COMPRESSION_RATIO,
    MAX_DOCX_UNCOMPRESSED_BYTES,
    MAX_PDF_PAGES,
)
from api.errors import ApiError
from api.validation import ValidatedUpload, validate_upload


def _clean_text(text: str) -> str:
    """清理提取结果，避免全是空白符时被误判为有内容。"""
    return re.sub(r"\n{3,}", "\n\n", (text or "")).strip()


def _extract_pdf_with_pdfplumber(file_bytes: bytes, max_pages: int) -> str:
    try:
        pdfplumber_module = importlib.import_module("pdfplumber")
    except ImportError:
        return ""
    try:
        parts = []
        with pdfplumber_module.open(io.BytesIO(file_bytes)) as pdf:
            if len(pdf.pages) > max_pages:
                raise ApiError(
                    422,
                    "PDF_TOO_MANY_PAGES",
                    "PDF 简历不能超过 10 页。",
                )
            for page in pdf.pages:
                parts.append(page.extract_text() or "")
        return _clean_text("\n".join(parts))
    except ApiError:
        raise
    except Exception:
        return ""


def _extract_pdf_with_pypdf(file_bytes: bytes, max_pages: int) -> str:
    try:
        pypdf_module = importlib.import_module("pypdf")
    except ImportError:
        return ""
    try:
        parts = []
        reader = pypdf_module.PdfReader(io.BytesIO(file_bytes))
        if len(reader.pages) > max_pages:
            raise ApiError(
                422,
                "PDF_TOO_MANY_PAGES",
                "PDF 简历不能超过 10 页。",
            )
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return _clean_text("\n".join(parts))
    except ApiError:
        raise
    except Exception:
        return ""


def _extract_pdf(raw: bytes, max_pages: int) -> str:
    """先检查 PDF 页数，再提取文字，并在首选解析器失败时回退。"""
    text = _extract_pdf_with_pdfplumber(raw, max_pages)
    if text:
        return text
    return _extract_pdf_with_pypdf(raw, max_pages)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """优先用 pdfplumber，失败后回退到 pypdf。"""
    return _extract_pdf(file_bytes, MAX_PDF_PAGES)


def _validate_docx_archive(raw: bytes) -> None:
    """在 python-docx 展开压缩包前检查解压总量和单项压缩比。"""
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()

    total_uncompressed = sum(entry.file_size for entry in entries)
    if total_uncompressed > MAX_DOCX_UNCOMPRESSED_BYTES:
        raise ApiError(
            422,
            "DOCX_UNCOMPRESSED_TOO_LARGE",
            "DOCX 解压后内容不能超过 20 MB。",
        )

    for entry in entries:
        ratio = entry.file_size / max(entry.compress_size, 1)
        if ratio > MAX_DOCX_COMPRESSION_RATIO:
            raise ApiError(
                422,
                "DOCX_COMPRESSION_RATIO_TOO_HIGH",
                "DOCX 文件压缩比超过安全限制。",
            )


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
    except ImportError:
        return ""
    try:
        document = docx.Document(io.BytesIO(file_bytes))
        parts = [p.text for p in document.paragraphs if p.text.strip()]
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        parts.append(cell.text)
        return _clean_text("\n".join(parts))
    except ApiError:
        raise
    except Exception:
        return ""


def parse_validated_resume(upload: ValidatedUpload) -> str:
    """解析已通过上传校验的简历，返回非空纯文本。"""
    try:
        if upload.kind == "txt":
            text = _clean_text(upload.raw.decode("utf-8", errors="ignore"))
        elif upload.kind == "pdf":
            text = _extract_pdf(upload.raw, MAX_PDF_PAGES)
        elif upload.kind == "docx":
            _validate_docx_archive(upload.raw)
            text = extract_text_from_docx(upload.raw)
        else:
            raise ApiError(
                415,
                "UNSUPPORTED_FILE_TYPE",
                "请上传 PDF、DOCX 或 TXT 文件。",
            )
    except ApiError:
        raise
    except Exception:
        text = ""

    text = _clean_text(text)
    if not text:
        raise ApiError(
            422,
            "RESUME_TEXT_EMPTY",
            "没有提取到可用文字。扫描件、加密文件或损坏文件暂不支持。",
            supported_action="请上传可复制文字的 PDF、DOCX 或 TXT。",
        )
    return text


def parse_resume(filename: str, file_bytes: bytes) -> str:
    """临时兼容入口：先校验上传，再调用安全解析器。"""
    upload = validate_upload(filename, None, file_bytes)
    return parse_validated_resume(upload)
