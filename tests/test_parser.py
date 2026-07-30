import sys
import types
import unittest
from unittest.mock import patch

from api import parser


class _FakePdfPlumber(types.SimpleNamespace):
    @staticmethod
    def open(_stream):
        raise RuntimeError("pdfplumber failed")


class _FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class _FakePdfReader:
    def __init__(self, _stream):
        self.pages = [_FakePage("教育背景"), _FakePage("Python 项目经验")]


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


if __name__ == "__main__":
    unittest.main()
