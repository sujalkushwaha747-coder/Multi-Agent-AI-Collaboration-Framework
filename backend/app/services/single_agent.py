import time
from dataclasses import dataclass, field
from typing import Any

from app.core.config import Settings, get_settings
from app.retrieval.service import RetrievalService
from app.services.llm_service import OllamaLLMService


@dataclass
class SingleAgentRun:
    response: str
    execution_time_seconds: float
    model_name: str
    retrieval_context: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SingleAgentService:
    def __init__(
        self,
        llm: OllamaLLMService | None = None,
        retrieval: RetrievalService | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or get_settings()
        self.llm = llm or OllamaLLMService(self.settings)
        self.retrieval = retrieval or RetrievalService(self.settings)

    async def run(
        self,
        *,
        prompt: str,
        task_category: str,
        document_ids: list[str] | None = None,
        top_k: int | None = None,
    ) -> SingleAgentRun:
        start = time.perf_counter()
        context_results = self.retrieval.search(
            prompt,
            document_ids=document_ids or [],
            top_k=top_k or self.settings.retrieval_top_k,
        )
        context = [
            {
                "document_id": item.document_id,
                "chunk_id": item.chunk_id,
                "chunk_index": item.chunk_index,
                "text": item.text,
                "score": item.score,
                "metadata": item.metadata,
            }
            for item in context_results
        ]
        context_text = "\n\n".join(
            f"[Context {index + 1}] {item['text']}" for index, item in enumerate(context)
        )
        system_prompt = (
            "You are the Single-Agent architecture in ShodhAI. Solve the user's task independently. "
            "Use retrieved context when it is relevant, state assumptions when evidence is unavailable, "
            "and do not simulate a multi-agent workflow."
        )
        user_message = (
            f"Task category: {task_category}\n"
            f"User prompt:\n{prompt}\n\n"
            f"Retrieved context:\n{context_text or 'No retrieved context available.'}\n\n"
            "Generate the final response."
        )
        generation = await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_message,
        )
        return SingleAgentRun(
            response=generation.text,
            execution_time_seconds=time.perf_counter() - start,
            model_name=generation.model,
            retrieval_context=context,
            metadata=generation.metadata,
        )

