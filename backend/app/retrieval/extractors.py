from pathlib import Path

from app.core.exceptions import InvalidUploadError


def extract_text(file_path: Path, extension: str) -> str:
    ext = extension.lower()
    if ext == ".txt":
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise InvalidUploadError("PDF extraction requires the pypdf package.") from exc
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError as exc:
            raise InvalidUploadError("DOCX extraction requires the python-docx package.") from exc
        doc = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    raise InvalidUploadError("Unsupported document type.")

