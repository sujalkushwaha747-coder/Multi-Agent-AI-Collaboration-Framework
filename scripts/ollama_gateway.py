"""Token-protected local Ollama gateway for a temporary demo tunnel.

Run from the repository root:
  backend/.venv/bin/python -m uvicorn scripts.ollama_gateway:app --host 127.0.0.1 --port 11435
Set OLLAMA_API_KEY to a private random token of at least 32 characters first.
Only tags and non-streaming generation are forwarded to local Ollama.
"""
import hmac
import json
import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response


def create_gateway(token: str, transport=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app):
        if len(token) < 32:
            raise RuntimeError("Set OLLAMA_API_KEY to a private random token of at least 32 characters.")
        yield

    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

    @app.middleware("http")
    async def authenticate(request: Request, call_next):
        expected = f"Bearer {token}".encode()
        supplied = request.headers.get("authorization", "").encode()
        if len(token) < 32 or not hmac.compare_digest(supplied, expected):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
        return await call_next(request)

    async def proxy(method: str, path: str, payload=None):
        try:
            async with httpx.AsyncClient(transport=transport, timeout=600.0) as client:
                result = await client.request(method, f"http://127.0.0.1:11434{path}", json=payload)
        except httpx.RequestError:
            return JSONResponse(status_code=502, content={"detail": "Local Ollama is not reachable."})
        return Response(result.content, status_code=result.status_code,
                        media_type=result.headers.get("content-type", "application/json"))

    @app.get("/api/tags")
    async def tags():
        return await proxy("GET", "/api/tags")

    @app.post("/api/generate")
    async def generate(request: Request):
        body = bytearray()
        async for chunk in request.stream():
            body.extend(chunk)
            if len(body) > 2 * 1024 * 1024:
                return JSONResponse(status_code=413, content={"detail": "Request too large."})
        try:
            payload = json.loads(body)
            if not isinstance(payload, dict):
                raise ValueError
        except (ValueError, UnicodeDecodeError):
            return JSONResponse(status_code=400, content={"detail": "Expected a JSON object."})
        payload["stream"] = False
        return await proxy("POST", "/api/generate", payload)

    return app


app = create_gateway(os.environ.get("OLLAMA_API_KEY", ""))
