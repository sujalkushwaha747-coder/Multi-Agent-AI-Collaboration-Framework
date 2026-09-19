import pytest

from app.core.config import Settings
from app.services.llm_service import LLMGeneration, OllamaLLMService


@pytest.mark.asyncio
async def test_groq_failure_falls_back_to_ollama(monkeypatch):
    settings = Settings(
        llm_provider="auto",
        groq_api_key="test-key",
        database_url="sqlite:///:memory:",
    )
    service = OllamaLLMService(settings)

    async def fail_groq(**_):
        raise RuntimeError("groq unavailable")

    async def use_ollama(**kwargs):
        return LLMGeneration(
            text="fallback response",
            model="ollama:llama3:8b",
            duration_seconds=0.1,
            metadata={
                "provider": "ollama",
                "fallback_from_groq": str(kwargs["fallback_error"]),
            },
        )

    monkeypatch.setattr(service, "_generate_groq", fail_groq)
    monkeypatch.setattr(service, "_generate_ollama", use_ollama)

    generation = await service.generate(
        system_prompt="system",
        user_prompt="user",
    )

    assert generation.text == "fallback response"
    assert generation.metadata["provider"] == "ollama"
    assert "groq unavailable" in generation.metadata["fallback_from_groq"]
