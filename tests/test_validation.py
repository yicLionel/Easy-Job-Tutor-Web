import unittest

from api.errors import ApiError
from api.validation import validate_jd, validate_upload


class ValidationTests(unittest.TestCase):
    def test_jd_must_be_between_50_and_20000_characters(self):
        with self.assertRaisesRegex(ApiError, "至少 50"):
            validate_jd("Python developer")
        self.assertEqual(validate_jd("A" * 50), "A" * 50)
        with self.assertRaisesRegex(ApiError, "不能超过 20000"):
            validate_jd("A" * 20001)

    def test_upload_rejects_legacy_doc_and_files_over_5_mib(self):
        with self.assertRaisesRegex(ApiError, "PDF、DOCX 或 TXT"):
            validate_upload("resume.doc", "application/msword", b"doc")
        with self.assertRaisesRegex(ApiError, "5 MB"):
            validate_upload("resume.txt", "text/plain", b"x" * (5 * 1024 * 1024 + 1))

    def test_upload_rejects_fake_pdf_extension(self):
        with self.assertRaisesRegex(ApiError, "真实类型"):
            validate_upload("resume.pdf", "application/pdf", b"not-a-pdf")

    def test_upload_rejects_mime_mismatch(self):
        with self.assertRaisesRegex(ApiError, "MIME"):
            validate_upload("resume.pdf", "text/plain", b"%PDF-1.7")

    def test_upload_accepts_pdf_docx_and_txt_signatures(self):
        self.assertEqual(validate_upload("r.pdf", "application/pdf", b"%PDF-1.7").kind, "pdf")
        self.assertEqual(
            validate_upload(
                "r.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                b"PK\x03\x04data",
            ).kind,
            "docx",
        )
        self.assertEqual(validate_upload("r.txt", "text/plain", "简历".encode()).kind, "txt")
