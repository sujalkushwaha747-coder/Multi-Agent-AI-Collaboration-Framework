import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VectorRecord:
    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
    vector: list[float]
    metadata: dict = field(default_factory=dict)


@dataclass
class SearchResult:
    document_id: str
    chunk_id: str
    chunk_index: int
    text: str
    score: float
    metadata: dict


class FaissVectorStore:
    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path = self.index_dir / "chunks.json"
        self.index_path = self.index_dir / "index.faiss"
        self.records: list[VectorRecord] = []
        self._faiss = None
        self._index = None
        self._load_faiss()
        self._load()

    @property
    def backend(self) -> str:
        return "faiss" if self._faiss is not None else "numpy-fallback"

    def _load_faiss(self) -> None:
        try:
            import faiss
        except ImportError:
            logger.warning("faiss-cpu is not installed; vector search uses numpy fallback")
            self._faiss = None
            return
        self._faiss = faiss

    def _load(self) -> None:
        if self.metadata_path.exists():
            data = json.loads(self.metadata_path.read_text(encoding="utf-8"))
            self.records = [VectorRecord(**item) for item in data]
        self._rebuild_index()

    def _persist(self) -> None:
        self.metadata_path.write_text(
            json.dumps([record.__dict__ for record in self.records], indent=2),
            encoding="utf-8",
        )
        if self._faiss is not None and self._index is not None:
            self._faiss.write_index(self._index, str(self.index_path))

    def _rebuild_index(self) -> None:
        if not self.records:
            self._index = None
            return
        vectors = np.array([record.vector for record in self.records], dtype="float32")
        if self._faiss is None:
            self._index = vectors
            return
        index = self._faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        self._index = index

    def add_chunks(
        self,
        *,
        document_id: str,
        chunks: list[tuple[int, str]],
        vectors: list[list[float]],
        metadata: dict | None = None,
    ) -> int:
        self.remove_document(document_id, persist=False)
        for (chunk_index, text), vector in zip(chunks, vectors, strict=True):
            self.records.append(
                VectorRecord(
                    chunk_id=str(uuid4()),
                    document_id=document_id,
                    chunk_index=chunk_index,
                    text=text,
                    vector=vector,
                    metadata=metadata or {},
                )
            )
        self._rebuild_index()
        self._persist()
        return len(chunks)

    def remove_document(self, document_id: str, *, persist: bool = True) -> None:
        self.records = [record for record in self.records if record.document_id != document_id]
        self._rebuild_index()
        if persist:
            self._persist()

    def search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_ids: list[str] | None = None,
    ) -> list[SearchResult]:
        if not self.records or self._index is None:
            return []
        allowed = set(document_ids or [])
        query = np.array([query_vector], dtype="float32")
        if self._faiss is not None:
            scores, indices = self._index.search(query, min(top_k * 4, len(self.records)))
            pairs = zip(scores[0].tolist(), indices[0].tolist(), strict=False)
        else:
            matrix = self._index
            raw_scores = (matrix @ query[0]).tolist()
            ordered = np.argsort(raw_scores)[::-1][: top_k * 4]
            pairs = [(raw_scores[index], int(index)) for index in ordered]

        results: list[SearchResult] = []
        for score, index in pairs:
            if index < 0:
                continue
            record = self.records[index]
            if allowed and record.document_id not in allowed:
                continue
            results.append(
                SearchResult(
                    document_id=record.document_id,
                    chunk_id=record.chunk_id,
                    chunk_index=record.chunk_index,
                    text=record.text,
                    score=round(float(score), 4),
                    metadata=record.metadata,
                )
            )
            if len(results) >= top_k:
                break
        return results

