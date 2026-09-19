from app.agents.base import AgentBase, AgentOutput


class WriterAgent(AgentBase):
    name = "Writer Agent"
    system_prompt = (
        "You are the Writer Agent for ShodhAI. Produce the main answer from the research and plan. "
        "Be clear, structured, relevant, and avoid unsupported claims."
    )

    async def run(
        self,
        *,
        user_prompt: str,
        research_notes: str,
        plan: str,
        review_feedback: str | None = None,
    ) -> AgentOutput:
        feedback = (
            f"\nReviewer feedback to address:\n{review_feedback}\n"
            if review_feedback
            else ""
        )
        user_message = (
            f"Original prompt:\n{user_prompt}\n\n"
            f"Research notes:\n{research_notes}\n\n"
            f"Plan:\n{plan}\n"
            f"{feedback}\n"
            "Write the response now. Do not include hidden chain-of-thought."
        )
        return await self.complete(user_message, {"revision": bool(review_feedback)})

