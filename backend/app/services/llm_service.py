import asyncio
import time
from dataclasses import dataclass

import httpx

from app.core.config import Settings, get_settings
from app.core.exceptions import LLMUnavailableError
from app.services.prompting import render_prompt


@dataclass
class LLMGeneration:
    text: str
    model: str
    duration_seconds: float
    metadata: dict


class OllamaLLMService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def health_check(self) -> dict:
        groq = {"available": False, "configured_model": self.settings.groq_model}
        if self.settings.groq_api_key:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        f"{self.settings.groq_base_url}/models",
                        headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
                    )
                    response.raise_for_status()
                    models = response.json().get("data", [])
                    model_names = [model.get("id") for model in models]
                    groq = {
                        "available": True,
                        "configured_model": self.settings.groq_model,
                        "model_available": self.settings.groq_model in model_names,
                        "models": model_names,
                    }
            except Exception as exc:
                groq = {
                    "available": False,
                    "configured_model": self.settings.groq_model,
                    "model_available": False,
                    "error": str(exc),
                }
        else:
            groq["error"] = "GROQ_API_KEY is not configured."

        ollama = {"available": False, "configured_model": self.settings.ollama_model}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.settings.ollama_base_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                ollama = {
                    "available": True,
                    "configured_model": self.settings.ollama_model,
                    "model_available": self.settings.ollama_model in model_names,
                    "models": model_names,
                }
        except Exception as exc:
            ollama = {
                "available": False,
                "configured_model": self.settings.ollama_model,
                "model_available": False,
                "error": str(exc),
            }
        selected = "groq" if self._should_try_groq() and groq["available"] else "ollama"
        return {
            "provider_mode": self.settings.llm_provider,
            "selected_provider": selected,
            "groq": groq,
            "ollama": ollama,
        }

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMGeneration:
        if self._should_try_groq():
            try:
                return await self._generate_groq(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as exc:
                if self.settings.llm_provider == "groq":
                    last_error = exc
                else:
                    last_error = exc
        else:
            last_error = None

        try:
            return await self._generate_ollama(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                fallback_error=last_error,
            )
        except Exception as exc:
            if last_error:
                raise LLMUnavailableError(
                    "Groq and Ollama are both unavailable or failed to generate a response. "
                    f"Groq error: {last_error}. Ollama error: {exc}"
                ) from exc
            raise

    def _should_try_groq(self) -> bool:
        return bool(
            self.settings.llm_provider in {"auto", "groq"}
            and self.settings.groq_api_key
        )

    async def _generate_groq(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMGeneration:
        start = time.perf_counter()
        payload = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.settings.groq_temperature
            if temperature is None
            else temperature,
            "max_completion_tokens": max_tokens or self.settings.groq_max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.settings.groq_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.groq_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices") or []
            text = ""
            if choices:
                text = ((choices[0].get("message") or {}).get("content") or "").strip()
            if not text:
                raise LLMUnavailableError("Groq returned an empty response.")
            usage = data.get("usage") or {}
            return LLMGeneration(
                text=text,
                model=f"groq:{data.get('model') or self.settings.groq_model}",
                duration_seconds=time.perf_counter() - start,
                metadata={
                    "provider": "groq",
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
            )

    async def _generate_ollama(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        fallback_error: Exception | None = None,
    ) -> LLMGeneration:
        rendered_prompt = render_prompt(system_prompt, user_prompt)
        payload = {
            "model": self.settings.ollama_model,
            "prompt": rendered_prompt,
            "stream": False,
            "options": {
                "temperature": self.settings.ollama_temperature
                if temperature is None
                else temperature,
                "num_predict": max_tokens or self.settings.ollama_max_tokens,
            },
        }
        last_error: Exception | None = None
        for attempt in range(self.settings.ollama_retries + 1):
            start = time.perf_counter()
            try:
                async with httpx.AsyncClient(
                    timeout=self.settings.ollama_timeout_seconds
                ) as client:
                    response = await client.post(
                        f"{self.settings.ollama_base_url}/api/generate",
                        json=payload,
                    )
                    response.raise_for_status()
                    data = response.json()
                    text = (data.get("response") or "").strip()
                    if not text:
                        raise LLMUnavailableError("Ollama returned an empty response.")
                    return LLMGeneration(
                        text=text,
                        model=f"ollama:{self.settings.ollama_model}",
                        duration_seconds=time.perf_counter() - start,
                        metadata={
                            "provider": "ollama",
                            "fallback_from_groq": str(fallback_error)
                            if fallback_error
                            else None,
                            "eval_count": data.get("eval_count"),
                            "prompt_eval_count": data.get("prompt_eval_count"),
                            "total_duration": data.get("total_duration"),
                            "attempt": attempt + 1,
                        },
                    )
            except Exception as exc:
                last_error = exc
                if attempt < self.settings.ollama_retries:
                    await asyncio.sleep(0.75 * (attempt + 1))
        raise LLMUnavailableError(
            "Ollama is unavailable or the configured model could not generate a response. "
            f"Check OLLAMA_BASE_URL and pull {self.settings.ollama_model}. "
            f"Details: {last_error}"
        )
