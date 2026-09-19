import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import InvalidUploadError, http_not_found
from app.models.document import Document
from app.retrieval.service import RetrievalService

SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")


class DocumentService:
    def __init__(
        self,
        settings: Settings | None = None,
        retrieval: RetrievalService | None = None,
    ):
        self.settings = settings or get_settings()
        self._retrieval = retrieval
        self.settings.resolved_upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def retrieval(self) -> RetrievalService:
        if self._retrieval is None:
            self._retrieval = RetrievalService(self.settings)
        return self._retrieval

    async def upload(self, db: Session, upload: UploadFile) -> Document:
        original_name = upload.filename or "document"
        extension = Path(original_name).suffix.lower()
        if extension not in self.settings.allowed_file_extensions:
            raise InvalidUploadError(
                f"Unsupported file type. Allowed: {', '.join(self.settings.allowed_file_extensions)}"
            )
        content = await upload.read()
        if len(content) == 0:
            raise InvalidUploadError("Uploaded file is empty.")
        if len(content) > self.settings.max_file_size_bytes:
            raise InvalidUploadError(
                f"File exceeds the {self.settings.max_file_size_mb} MB limit."
            )
        safe_name = SAFE_FILENAME_RE.sub("_", Path(original_name).name)
        stored_name = f"{uuid4()}_{safe_name}"
        destination = self.settings.resolved_upload_dir / stored_name
        destination.write_bytes(content)
        document = Document(
            original_filename=original_name,
            stored_filename=stored_name,
            content_type=upload.content_type,
            file_extension=extension,
            file_size=len(content),
            status="uploaded",
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def list_documents(self, db: Session) -> list[Document]:
        return db.query(Document).order_by(Document.created_at.desc()).all()

    def get_document(self, db: Session, document_id: str) -> Document:
        document = db.get(Document, document_id)
        if not document:
            raise http_not_found("Document not found.")
        return document

    def index(self, db: Session, document_id: str) -> Document:
        document = self.get_document(db, document_id)
        return self.retrieval.index_document(db, document)

    def delete(self, db: Session, document_id: str) -> None:
        document = self.get_document(db, document_id)
        self.retrieval.delete_document(db, document)
