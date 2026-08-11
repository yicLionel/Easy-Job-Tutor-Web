import io
import sys
import types
import unittest
import zipfile
from unittest.mock import patch

import pdfplumber

from api import parser
from api.errors import ApiError
from api.validation import ValidatedUpload


class _FakePdfPlumber(types.SimpleNamespace):
    @staticmethod
    def open(_stream):
        raise RuntimeError("pdfplumber failed")


class _FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class _PageThatMustNotBeExtracted:
    def extract_text(self):
        raise AssertionError("page text was extracted before the page limit check")


class _FakePdfReader:
    def __init__(self, _stream):
        self.pages = [_FakePage("教育背景"), _FakePage("Python 项目经验")]


def _minimal_zip_bytes():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("word/document.xml", "")
    return stream.getvalue()


def _zip_entry(filename, file_size, compress_size):
    entry = zipfile.ZipInfo(filename)
    entry.file_size = file_size
    entry.compress_size = compress_size
    return entry


class ParserTests(unittest.TestCase):
    def test_parse_txt_cleans_whitespace(self):
        text = parser.parse_resume("resume.txt", b"\n\nhello\n\n\nworld\n")
        self.assertEqual(text, "hello\n\nworld")

    def test_pdf_falls_back_to_pypdf_when_pdfplumber_fails(self):
        fake_pypdf = types.SimpleNamespace(PdfReader=_FakePdfReader)
        with patch.dict(
            sys.modules,
            {
                "pdfplumber": _FakePdfPlumber(),
                "pypdf": fake_pypdf,
            },
        ):
            text = parser.extract_text_from_pdf(b"%PDF-fake")

        self.assertIn("教育背景", text)
        self.assertIn("Python 项目经验", text)

    def test_pdf_over_ten_pages_is_rejected_before_extraction(self):
        class _FakePdf:
            pages = [_PageThatMustNotBeExtracted()] * 11

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                return False

        with patch.object(pdfplumber, "open", return_value=_FakePdf()):
            with self.assertRaisesRegex(ApiError, "10 页") as caught:
                parser.parse_validated_resume(
                    ValidatedUpload("r.pdf", "pdf", b"%PDF-1.7")
                )

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(caught.exception.error_code, "PDF_TOO_MANY_PAGES")

    def test_docx_over_total_uncompressed_limit_is_rejected(self):
        entries = [
            _zip_entry("word/document.xml", 10 * 1024 * 1024, 1024 * 1024),
            _zip_entry("word/styles.xml", 10 * 1024 * 1024 + 1, 1024 * 1024),
        ]
        with patch.object(zipfile.ZipFile, "infolist", return_value=entries):
            with self.assertRaisesRegex(ApiError, "20 MB") as caught:
                parser.parse_validated_resume(
                    ValidatedUpload("r.docx", "docx", _minimal_zip_bytes())
                )

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(
            caught.exception.error_code, "DOCX_UNCOMPRESSED_TOO_LARGE"
        )

    def test_docx_over_compression_ratio_limit_is_rejected(self):
        entries = [_zip_entry("word/document.xml", 101, 1)]
        with patch.object(zipfile.ZipFile, "infolist", return_value=entries):
            with self.assertRaisesRegex(ApiError, "压缩比") as caught:
                parser.parse_validated_resume(
                    ValidatedUpload("r.docx", "docx", _minimal_zip_bytes())
                )

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(
            caught.exception.error_code, "DOCX_COMPRESSION_RATIO_TOO_HIGH"
        )

    def test_empty_text_has_explicit_parse_error(self):
        with self.assertRaisesRegex(ApiError, "没有提取到可用文字") as caught:
            parser.parse_validated_resume(
                ValidatedUpload("r.txt", "txt", b"   \n")
            )

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(caught.exception.error_code, "RESUME_TEXT_EMPTY")
        self.assertEqual(
            caught.exception.supported_action,
            "请上传可复制文字的 PDF、DOCX 或 TXT。",
        )

    def test_corrupt_docx_has_explicit_parse_error(self):
        with self.assertRaisesRegex(ApiError, "没有提取到可用文字") as caught:
            parser.parse_validated_resume(
                ValidatedUpload("r.docx", "docx", b"PK\x03\x04broken")
            )

        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(caught.exception.error_code, "RESUME_TEXT_EMPTY")

    def test_docx_extractor_does_not_swallow_api_error(self):
        failure = ApiError(422, "DOCX_LIMIT", "limit reached")
        with patch("docx.Document", side_effect=failure):
            with self.assertRaises(ApiError) as caught:
                parser.extract_text_from_docx(_minimal_zip_bytes())

        self.assertIs(caught.exception, failure)

    def test_legacy_doc_is_rejected(self):
        with self.assertRaises(ApiError) as caught:
            parser.parse_resume("legacy.doc", b"legacy word bytes")

        self.assertEqual(caught.exception.status_code, 415)
        self.assertEqual(caught.exception.error_code, "UNSUPPORTED_FILE_TYPE")

    def test_unknown_extension_has_no_parser_fallback(self):
        with self.assertRaises(ApiError) as caught:
            parser.parse_resume("resume.bin", b"%PDF-1.7")

        self.assertEqual(caught.exception.status_code, 415)
        self.assertEqual(caught.exception.error_code, "UNSUPPORTED_FILE_TYPE")


if __name__ == "__main__":
    unittest.main()
