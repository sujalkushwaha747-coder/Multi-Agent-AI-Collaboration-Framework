import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.deps import db_session
from app.api.routes.health import router
from app.core.config import Settings
from app.deployment import prepare_runtime


def deployment_settings(tmp_path, **overrides):
    values = dict(
        _env_file=None,
        app_env="production",
        llm_provider="groq",
        groq_api_key="test-key",
        cors_origins="https://library-demo.vercel.app",
        database_url=f"sqlite:///{tmp_path / 'db' / 'experiments.db'}",
        upload_dir=str(tmp_path / "uploads"),
        faiss_index_path=str(tmp_path / "faiss"),
    )
    values.update(overrides)
    return Settings(**values)


def test_production_prepares_storage(tmp_path):
    settings = deployment_settings(tmp_path)
    prepare_runtime(settings)
    assert (tmp_path / "db").is_dir()
    assert settings.resolved_upload_dir.is_dir()
    assert settings.resolved_faiss_index_path.is_dir()


@pytest.mark.parametrize("overrides", [
    {"groq_api_key": None},
    {"cors_origins": ""},
    {"cors_origins": "http://localhost:5173"},
    {"cors_origins": "https://demo.vercel.app/"},
    {"cors_origins": "https://demo.vercel.app/path"},
    {"database_url": "sqlite:///./temporary.db"},
])
def test_production_rejects_incomplete_configuration(tmp_path, overrides):
    with pytest.raises(ValueError):
        prepare_runtime(deployment_settings(tmp_path, **overrides))


def test_health_probes_do_not_contact_providers():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    app = FastAPI()
    app.include_router(router, prefix="/api")

    def session():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[db_session] = session
    with TestClient(app) as client:
        assert client.get("/api/health/live").json() == {"status": "ok"}
        assert client.get("/api/health/ready").json()["database"]["available"] is True

        class FailedDatabase:
            def execute(self, *_):
                raise RuntimeError("private connection details")

        app.dependency_overrides[db_session] = lambda: FailedDatabase()
        failed = client.get("/api/health/ready")
        assert failed.status_code == 503
        assert "private" not in failed.text
    engine.dispose()
