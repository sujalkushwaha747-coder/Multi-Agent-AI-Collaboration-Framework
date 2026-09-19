from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ShodhAI"
    app_env: str = "development"
    api_prefix: str = "/api"
    log_level: str = "INFO"
    llm_provider: Literal["auto", "ollama", "groq"] = "auto"

    database_url: str = (
        "mysql+pymysql://username:password@localhost:3306/shodhai"
    )

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:8b"
    ollama_temperature: float = 0.2
    ollama_max_tokens: int = 2048
    ollama_timeout_seconds: float = 120.0
    ollama_retries: int = 1

    groq_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-20b"
    groq_temperature: float = 0.2
    groq_max_tokens: int = 2048
    groq_timeout_seconds: float = 60.0

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_provider: Literal["auto", "sentence-transformers", "hashing"] = "auto"
    embedding_dimension: int = 384

    faiss_index_path: str = "./data/faiss"
    upload_dir: str = "./data/uploads"
    max_file_size_mb: int = 20
    allowed_file_extensions: list[str] = Field(
        default_factory=lambda: [".pdf", ".txt", ".docx"]
    )

    cors_origins: str = "http://localhost:5173"
    cors_origin_regex: str | None = None
    max_prompt_chars: int = 12000
    max_revision_attempts: int = 1
    retrieval_top_k: int = 4

    weight_accuracy: float = 0.25
    weight_quality: float = 0.25
    weight_completeness: float = 0.20
    weight_hallucination: float = 0.20
    weight_execution_time: float = 0.10

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[3]

    @property
    def resolved_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_cors_origin_regex(self) -> str | None:
        if self.cors_origin_regex:
            return self.cors_origin_regex
        if self.app_env == "development":
            return r"https?://(localhost|127\.0\.0\.1):\d+"
        return None

    @property
    def resolved_faiss_index_path(self) -> Path:
        path = Path(self.faiss_index_path)
        return path if path.is_absolute() else self.project_root / path

    @property
    def resolved_upload_dir(self) -> Path:
        path = Path(self.upload_dir)
        return path if path.is_absolute() else self.project_root / path

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def overall_weights(self) -> dict[str, float]:
        return {
            "accuracy": self.weight_accuracy,
            "quality": self.weight_quality,
            "completeness": self.weight_completeness,
            "hallucination": self.weight_hallucination,
            "execution_time": self.weight_execution_time,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
