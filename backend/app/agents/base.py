import time
from dataclasses import dataclass, field
from typing import Any

from app.services.llm_service import OllamaLLMService


@dataclass
class AgentOutput:
    agent_name: str
    output: str
    summary: str
    duration_seconds: float
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentBase:
    name = "Agent"
    system_prompt = "You are a helpful academic AI assistant."

    def __init__(self, llm: OllamaLLMService):
        self.llm = llm

    async def complete(self, user_prompt: str, metadata: dict[str, Any] | None = None) -> AgentOutput:
        start = time.perf_counter()
        generation = await self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
        )
        duration = time.perf_counter() - start
        output = generation.text.strip()
        return AgentOutput(
            agent_name=self.name,
            output=output,
            summary=summarize_output(output),
            duration_seconds=duration,
            metadata={
                "model": generation.model,
                "llm_duration_seconds": generation.duration_seconds,
                **generation.metadata,
                **(metadata or {}),
            },
        )


def summarize_output(text: str, limit: int = 240) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."

