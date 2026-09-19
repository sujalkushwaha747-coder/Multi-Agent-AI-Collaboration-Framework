from pathlib import Path

import pytest

from app.core.config import Settings
from app.database.base import Base
from app.models import Experiment  # noqa: F401
from app.services.experiment_service import ExperimentService
from app.services.multi_agent import MultiAgentRun
from app.services.single_agent import SingleAgentRun
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class FakeSingle:
    async def run(self, **kwargs):
        return SingleAgentRun(
            response="RAG retrieves context before generation.",
            execution_time_seconds=1.0,
            model_name="fake",
            retrieval_context=[],
            metadata={},
        )


class FakeMulti:
    async def run(self, **kwargs):
        return MultiAgentRun(
            response="RAG retrieves evidence before generation and verifies the answer.",
            execution_time_seconds=2.0,
            model_name="fake",
            revision_attempts=0,
            retrieval_context=[],
            agent_runs=[
                {
                    "agent_name": "Research Agent",
                    "sequence": 1,
                    "status": "completed",
                    "duration_seconds": 0.1,
                    "summary": "researched",
                    "output": "notes",
                    "metadata_json": {},
                }
            ],
            metadata={},
        )


@pytest.fixture()
def db_session(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.mark.asyncio
async def test_experiment_run_both_stores_results(db_session) -> None:
    settings = Settings(database_url="sqlite:///:memory:", embedding_provider="hashing")
    service = ExperimentService(
        settings=settings,
        single_agent=FakeSingle(),
        multi_agent=FakeMulti(),
    )
    experiment = service.create(
        db_session,
        prompt="Explain RAG.",
        task_category="academic",
    )
    completed = await service.run_both(db_session, experiment)
    assert completed.status == "completed"
    assert completed.single_result is not None
    assert completed.multi_result is not None
    assert completed.evaluation is not None
    assert completed.agent_runs[0].agent_name == "Research Agent"

