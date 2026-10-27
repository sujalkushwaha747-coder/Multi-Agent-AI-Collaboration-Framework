import pytest
import httpx

from app.core.config import Settings
from app.core.exceptions import LLMUnavailableError
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


@pytest.mark.asyncio
async def test_cloud_failure_does_not_try_local_ollama(monkeypatch):
    service = OllamaLLMService(Settings(
        _env_file=None, llm_provider="groq", groq_api_key="test-key",
        ollama_fallback_enabled=False,
    ))

    async def fail_groq(**_):
        raise RuntimeError("rate limit reached")

    async def unexpected_ollama(**_):
        pytest.fail("Cloud configuration must not call Ollama")

    monkeypatch.setattr(service, "_generate_groq", fail_groq)
    monkeypatch.setattr(service, "_generate_ollama", unexpected_ollama)
    with pytest.raises(LLMUnavailableError, match="rate limit reached"):
        await service.generate(system_prompt="system", user_prompt="task")


@pytest.mark.asyncio
async def test_missing_cloud_key_fails_before_network(monkeypatch):
    service = OllamaLLMService(Settings(
        _env_file=None, llm_provider="groq", groq_api_key=None,
        ollama_fallback_enabled=False,
    ))

    async def unexpected_ollama(**_):
        pytest.fail("Missing cloud key must not call Ollama")

    monkeypatch.setattr(service, "_generate_ollama", unexpected_ollama)
    with pytest.raises(LLMUnavailableError, match="GROQ_API_KEY"):
        await service.generate(system_prompt="system", user_prompt="task")


@pytest.mark.asyncio
async def test_real_http_fallback_sends_gateway_token(monkeypatch):
    seen = []
    token = "private-test-token-12345678901234567890"
    service = OllamaLLMService(Settings(
        _env_file=None, llm_provider="auto", groq_api_key="fake-groq-key",
        ollama_api_key=token, ollama_base_url="https://demo.trycloudflare.com/",
        ollama_fallback_enabled=True, ollama_retries=0,
    ))

    def respond(request):
        seen.append(str(request.url))
        if request.url.host == "api.groq.com":
            return httpx.Response(429, json={"error": "rate limit"})
        assert request.headers["authorization"] == f"Bearer {token}"
        return httpx.Response(200, json={"response": "Ollama fallback answer"})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda **kw: real_client(transport=httpx.MockTransport(respond), **kw))
    result = await service.generate(system_prompt="system", user_prompt="question")
    assert result.text == "Ollama fallback answer"
    assert result.metadata["provider"] == "ollama"
    assert "429" in result.metadata["fallback_from_groq"]
    assert seen[-1] == "https://demo.trycloudflare.com/api/generate"
    health = await service._ollama_health()
    assert health["available"] is True
