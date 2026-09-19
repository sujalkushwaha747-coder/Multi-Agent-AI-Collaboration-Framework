from app.agents.base import AgentBase, AgentOutput


class VerifierAgent(AgentBase):
    name = "Verifier Agent"
    system_prompt = (
        "You are the Verifier Agent for ShodhAI. Verify consistency with evidence when available, "
        "check the original requirements, identify unsupported factual claims, and produce the final verified response. "
        "Do not expose private reasoning."
    )

    async def run(
        self,
        *,
        user_prompt: str,
        draft: str,
        review: str,
        retrieved_context: list[dict],
    ) -> AgentOutput:
        context = "\n\n".join(
            f"[Chunk {index + 1}] {item.get('text', '')}"
            for index, item in enumerate(retrieved_context)
        )
        user_message = (
            f"Original prompt:\n{user_prompt}\n\n"
            f"Latest draft:\n{draft}\n\n"
            f"Reviewer findings:\n{review}\n\n"
            f"Evidence context:\n{context or 'No retrieved evidence supplied.'}\n\n"
            "Return sections: Final response, Verification findings, Verification status."
        )
        return await self.complete(user_message, {"context_chunks": len(retrieved_context)})

