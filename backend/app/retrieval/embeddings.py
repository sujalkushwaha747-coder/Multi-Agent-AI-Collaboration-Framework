import hashlib
import logging
import math
from dataclasses import dataclass

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    vectors: list[list[float]]
    provider: str
    model: str


class HashingEmbeddingProvider:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.model = f"hashing-{dimension}"

    def embed(self, texts: list[str]) -> EmbeddingResult:
        vectors = [self._embed_one(text) for text in texts]
        return EmbeddingResult(vectors=vectors, provider="hashing", model=self.model)

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> EmbeddingResult:
        vectors = self.model.encode(texts, normalize_embeddings=True).tolist()
        return EmbeddingResult(
            vectors=vectors,
            provider="sentence-transformers",
            model=self.model_name,
        )


class EmbeddingService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._provider = self._build_provider()

    def _build_provider(self):
        if self.settings.embedding_provider == "hashing":
            return HashingEmbeddingProvider(self.settings.embedding_dimension)
        try:
            return SentenceTransformerEmbeddingProvider(self.settings.embedding_model)
        except ImportError:
            if self.settings.embedding_provider == "sentence-transformers":
                raise
            logger.warning(
                "sentence-transformers not installed; using deterministic hashing embeddings"
            )
            return HashingEmbeddingProvider(self.settings.embedding_dimension)

    def embed(self, texts: list[str]) -> EmbeddingResult:
        return self._provider.embed(texts)

