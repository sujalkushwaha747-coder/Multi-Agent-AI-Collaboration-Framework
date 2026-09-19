from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import RetrievalError
from app.models.document import Document
from app.retrieval.chunking import chunk_text
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.extractors import extract_text
from app.retrieval.faiss_store import FaissVectorStore, SearchResult


class RetrievalService:
    def __init__(
        self,
        settings: Settings | None = None,
        embeddings: EmbeddingService | None = None,
        vector_store: FaissVectorStore | None = None,
    ):
        self.settings = settings or get_settings()
        self.embeddings = embeddings or EmbeddingService(self.settings)
        self.vector_store = vector_store or FaissVectorStore(
            self.settings.resolved_faiss_index_path
        )

    def index_document(self, db: Session, document: Document) -> Document:
        file_path = self.settings.resolved_upload_dir / document.stored_filename
        try:
            text = extract_text(Path(file_path), document.file_extension)
            chunks = chunk_text(text)
            if not chunks:
                raise RetrievalError("No readable text was found in this document.")
            embedding_result = self.embeddings.embed([chunk.text for chunk in chunks])
            count = self.vector_store.add_chunks(
                document_id=document.id,
                chunks=[(chunk.chunk_index, chunk.text) for chunk in chunks],
                vectors=embedding_result.vectors,
                metadata={
                    "filename": document.original_filename,
                    "embedding_provider": embedding_result.provider,
                    "embedding_model": embedding_result.model,
                    "vector_backend": self.vector_store.backend,
                },
            )
            document.status = "indexed"
            document.chunk_count = count
            document.error_message = None
            document.indexed_at = datetime.now(timezone.utc)
        except Exception as exc:
            document.status = "failed"
            document.error_message = str(exc)
            db.add(document)
            db.commit()
            raise
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def delete_document(self, db: Session, document: Document) -> None:
        self.vector_store.remove_document(document.id)
        file_path = self.settings.resolved_upload_dir / document.stored_filename
        if file_path.exists():
            file_path.unlink()
        db.delete(document)
        db.commit()

    def search(
        self, query: str, *, document_ids: list[str] | None = None, top_k: int | None = None
    ) -> list[SearchResult]:
        if not query.strip():
            return []
        embedding = self.embeddings.embed([query]).vectors[0]
        return self.vector_store.search(
            embedding,
            top_k=top_k or self.settings.retrieval_top_k,
            document_ids=document_ids,
        )

