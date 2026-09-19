from app.agents.base import AgentBase, AgentOutput


class ReviewerAgent(AgentBase):
    name = "Reviewer Agent"
    system_prompt = (
        "You are the Reviewer Agent for ShodhAI. Critically review the draft for completeness, "
        "relevance, clarity, unsupported claims, and missing requirements. Return a concise review. "
        "End with exactly one line: REVISION_REQUIRED: yes or REVISION_REQUIRED: no."
    )

    async def run(self, *, user_prompt: str, draft: str, plan: str) -> AgentOutput:
        user_message = (
            f"Original prompt:\n{user_prompt}\n\n"
            f"Plan:\n{plan}\n\n"
            f"Draft response:\n{draft}\n\n"
            "Review the draft and decide whether one revision is required."
        )
        return await self.complete(user_message)


def parse_revision_required(review: str) -> bool:
    lowered = review.lower()
    if "revision_required: yes" in lowered:
        return True
    if "revision_required: no" in lowered:
        return False
    serious_markers = ["serious", "major issue", "unsupported", "missing requirement"]
    return any(marker in lowered for marker in serious_markers)

