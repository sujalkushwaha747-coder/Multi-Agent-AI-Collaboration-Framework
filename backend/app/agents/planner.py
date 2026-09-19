from app.agents.base import AgentBase, AgentOutput


class PlannerAgent(AgentBase):
    name = "Planner Agent"
    system_prompt = (
        "You are the Planner Agent for ShodhAI. Convert research notes into a clear response plan, "
        "required sections, key points, and constraints. Keep the output concise and structured."
    )

    async def run(self, *, user_prompt: str, research_notes: str) -> AgentOutput:
        user_message = (
            f"Original prompt:\n{user_prompt}\n\n"
            f"Research notes:\n{research_notes}\n\n"
            "Create a structured execution plan for the writer. Include required sections, key points, and constraints."
        )
        return await self.complete(user_message)

