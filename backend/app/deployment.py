"""Validate production configuration before migrations or serving traffic."""
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy.engine import make_url

from app.core.config import Settings, get_settings


def prepare_runtime(settings: Settings) -> None:
    if settings.app_env != "production":
        raise ValueError("Production startup requires APP_ENV=production.")
    if settings.llm_provider in {"groq", "auto"} and not settings.groq_api_key:
        raise ValueError("Set GROQ_API_KEY in the backend hosting environment.")
    if not settings.resolved_cors_origins:
        raise ValueError("Set CORS_ORIGINS to your deployed frontend HTTPS origin.")
    for origin in settings.resolved_cors_origins:
        parsed = urlsplit(origin)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.path or
                parsed.query or parsed.fragment or parsed.username or
                parsed.hostname in {"localhost", "127.0.0.1", "::1"}):
            raise ValueError("CORS_ORIGINS must contain exact public HTTPS origins without a trailing slash.")
    paths = [settings.resolved_upload_dir, settings.resolved_faiss_index_path]
    url = make_url(settings.database_url)
    if url.get_backend_name() == "sqlite":
        if not url.database or not Path(url.database).is_absolute():
            raise ValueError("Production SQLite requires an absolute path on persistent storage.")
        paths.append(Path(url.database).parent)
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    prepare_runtime(get_settings())
