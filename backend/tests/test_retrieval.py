from pathlib import Path

from app.retrieval.chunking import chunk_text
from app.retrieval.embeddings import HashingEmbeddingProvider
from app.retrieval.faiss_store import FaissVectorStore


def test_chunk_text_creates_overlapping_chunks() -> None:
    text = "Sentence one. " * 120
    chunks = chunk_text(text, chunk_size=160, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert all(chunk.text for chunk in chunks)


def test_vector_store_add_search_and_delete(tmp_path: Path) -> None:
    provider = HashingEmbeddingProvider(dimension=64)
    chunks = [(0, "retrieval augmented generation uses external context")]
    vectors = provider.embed([chunks[0][1]]).vectors
    store = FaissVectorStore(tmp_path)
    store.add_chunks(
        document_id="doc-1",
        chunks=chunks,
        vectors=vectors,
        metadata={"filename": "sample.txt"},
    )
    query = provider.embed(["external context retrieval"]).vectors[0]
    results = store.search(query, top_k=1)
    assert len(results) == 1
    assert results[0].document_id == "doc-1"
    store.remove_document("doc-1")
    assert store.search(query, top_k=1) == []

