from dataclasses import dataclass
from pathlib import Path

from api.config import MAX_JD_CHARS, MAX_UPLOAD_BYTES, MIN_JD_CHARS
from api.errors import ApiError


@dataclass(frozen=True)
class ValidatedUpload:
    filename: str
    kind: str
    raw: bytes


def validate_jd(text: str | None) -> str:
    value = (text or "").strip()
    if len(value) < MIN_JD_CHARS:
        raise ApiError(
            400,
            "JD_TOO_SHORT",
            "岗位 JD 至少 50 个字符。",
            supported_action="请粘贴完整岗位描述。",
        )
    if len(value) > MAX_JD_CHARS:
        raise ApiError(
            400,
            "JD_TOO_LONG",
            "岗位 JD 不能超过 20000 个字符。",
            supported_action="请删除无关页面内容后重试。",
        )
    return value


def validate_upload(filename: str, content_type: str | None, raw: bytes) -> ValidatedUpload:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ApiError(413, "FILE_TOO_LARGE", "简历文件不能超过 5 MB。")
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise ApiError(415, "UNSUPPORTED_FILE_TYPE", "请上传 PDF、DOCX 或 TXT 文件。")
    allowed_mime = {
        ".pdf": {"application/pdf"},
        ".docx": {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
        ".txt": {"text/plain"},
    }
    normalized_mime = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized_mime and normalized_mime not in allowed_mime[suffix]:
        raise ApiError(415, "FILE_MIME_MISMATCH", "文件扩展名与 MIME 类型不一致。")
    signatures = {
        ".pdf": raw.startswith(b"%PDF-"),
        ".docx": raw.startswith(b"PK\x03\x04"),
        ".txt": b"\x00" not in raw[:1024],
    }
    if not signatures[suffix]:
        raise ApiError(415, "FILE_SIGNATURE_MISMATCH", "文件扩展名与真实类型不一致。")
    return ValidatedUpload(filename=filename, kind=suffix[1:], raw=raw)
