from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str


def chunk_text(text: str, *, chunk_size: int = 900, overlap: int = 120) -> list[TextChunk]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        if end < len(cleaned):
            sentence_end = cleaned.rfind(".", start, end)
            if sentence_end > start + chunk_size * 0.55:
                end = sentence_end + 1
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(TextChunk(chunk_index=index, text=chunk))
            index += 1
        if end == len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks

