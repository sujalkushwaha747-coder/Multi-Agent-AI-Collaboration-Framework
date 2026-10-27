import importlib.util
import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

spec = importlib.util.spec_from_file_location(
    "ollama_gateway", Path(__file__).resolve().parents[2] / "scripts/ollama_gateway.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
TOKEN = "test-gateway-token-with-more-than-32-characters"


def test_gateway_authentication_and_forwarding():
    seen = []

    def upstream(request):
        seen.append(request)
        assert request.url.host == "127.0.0.1"
        assert request.url.port == 11434
        if request.method == "POST":
            assert json.loads(request.content)["stream"] is False
            return httpx.Response(200, json={"response": "answer"})
        return httpx.Response(200, json={"models": [{"name": "llama3:8b"}]})

    app = module.create_gateway(TOKEN, httpx.MockTransport(upstream))
    with TestClient(app) as client:
        assert client.get("/api/tags").status_code == 401
        assert client.get("/api/tags", headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert not seen
        headers = {"Authorization": f"Bearer {TOKEN}"}
        assert client.get("/api/tags", headers=headers).json()["models"][0]["name"] == "llama3:8b"
        assert client.post("/api/generate", headers=headers, json={"model": "llama3:8b", "stream": True}).json()["response"] == "answer"
        assert client.post("/api/pull", headers=headers, json={}).status_code == 404
        assert client.post("/api/generate", headers=headers, content="bad json").status_code == 400
        assert client.post("/api/generate", headers=headers, content="x" * (2 * 1024 * 1024 + 1)).status_code == 413


def test_gateway_refuses_missing_token():
    with pytest.raises(RuntimeError, match="OLLAMA_API_KEY"):
        with TestClient(module.create_gateway("")):
            pass
