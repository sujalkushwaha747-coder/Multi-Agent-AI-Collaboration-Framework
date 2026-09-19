from app.agents.base import AgentBase, AgentOutput


class ResearchAgent(AgentBase):
    name = "Research Agent"
    system_prompt = (
        "You are the Research Agent for ShodhAI. Extract concise research notes, "
        "retrieved evidence, useful facts, and information gaps. Do not expose private reasoning."
    )

    async def run(
        self, *, user_prompt: str, task_category: str, retrieved_context: list[dict]
    ) -> AgentOutput:
        context = "\n\n".join(
            f"[Chunk {index + 1}] {item.get('text', '')}"
            for index, item in enumerate(retrieved_context)
        )
        user_message = (
            f"Task category: {task_category}\n"
            f"Original prompt:\n{user_prompt}\n\n"
            f"Retrieved context:\n{context or 'No retrieved documents were supplied.'}\n\n"
            "Return sections: Research findings, Retrieved context used, Important facts, Information gaps."
        )
        return await self.complete(user_message, {"context_chunks": len(retrieved_context)})

