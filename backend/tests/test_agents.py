import pytest

from app.core.config import Settings
from app.services.llm_service import LLMGeneration
from app.services.multi_agent import MultiAgentService


class FakeLLM:
    async def generate(self, *, system_prompt: str, user_prompt: str, **kwargs):
        if "Research Agent" in system_prompt:
            text = "Research findings: RAG combines retrieval and generation. Information gaps: none."
        elif "Planner Agent" in system_prompt:
            text = "Plan: define RAG, explain retrieval, explain benefits, mention limitations."
        elif "Writer Agent" in system_prompt:
            text = "RAG retrieves relevant context before generation, improving grounding and traceability."
        elif "Reviewer Agent" in system_prompt:
            text = "Review findings: complete and clear.\nREVISION_REQUIRED: no"
        else:
            text = "Final response: RAG improves answer grounding by using retrieved evidence.\nVerification status: verified"
        return LLMGeneration(
            text=text,
            model="fake-model",
            duration_seconds=0.01,
            metadata={"fake": True},
        )


class FakeRetrieval:
    def search(self, query: str, *, document_ids=None, top_k=None):
        return []


@pytest.mark.asyncio
async def test_multi_agent_workflow_runs_all_roles() -> None:
    settings = Settings(
        database_url="sqlite:///:memory:",
        embedding_provider="hashing",
        max_revision_attempts=1,
    )
    service = MultiAgentService(
        llm=FakeLLM(),
        retrieval=FakeRetrieval(),
        settings=settings,
    )
    result = await service.run(
        prompt="Explain Retrieval-Augmented Generation.",
        task_category="academic",
    )
    names = [run["agent_name"] for run in result.agent_runs]
    assert names == [
        "Research Agent",
        "Planner Agent",
        "Writer Agent",
        "Reviewer Agent",
        "Verifier Agent",
    ]
    assert "Final response" in result.response

