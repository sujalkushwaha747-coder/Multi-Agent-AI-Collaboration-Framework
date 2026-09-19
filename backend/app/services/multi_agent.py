import logging
import time
from dataclasses import dataclass, field
from typing import Any, TypedDict

from app.agents.base import AgentOutput
from app.agents.planner import PlannerAgent
from app.agents.research import ResearchAgent
from app.agents.reviewer import ReviewerAgent, parse_revision_required
from app.agents.verifier import VerifierAgent
from app.agents.writer import WriterAgent
from app.core.config import Settings, get_settings
from app.core.exceptions import ShodhAIError
from app.retrieval.service import RetrievalService
from app.services.llm_service import OllamaLLMService

logger = logging.getLogger(__name__)


class MultiAgentState(TypedDict, total=False):
    user_prompt: str
    task_category: str
    retrieved_context: list[dict[str, Any]]
    research_notes: str
    plan: str
    draft: str
    review: str
    verification: str
    final_response: str
    revision_required: bool
    revision_count: int
    agent_runs: list[dict[str, Any]]
    errors: list[str]
    status: str


@dataclass
class MultiAgentRun:
    response: str
    execution_time_seconds: float
    model_name: str
    revision_attempts: int
    retrieval_context: list[dict[str, Any]] = field(default_factory=list)
    agent_runs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class MultiAgentService:
    def __init__(
        self,
        llm: OllamaLLMService | None = None,
        retrieval: RetrievalService | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or get_settings()
        self.llm = llm or OllamaLLMService(self.settings)
        self.retrieval = retrieval or RetrievalService(self.settings)
        self.research_agent = ResearchAgent(self.llm)
        self.planner_agent = PlannerAgent(self.llm)
        self.writer_agent = WriterAgent(self.llm)
        self.reviewer_agent = ReviewerAgent(self.llm)
        self.verifier_agent = VerifierAgent(self.llm)

    async def run(
        self,
        *,
        prompt: str,
        task_category: str,
        document_ids: list[str] | None = None,
        top_k: int | None = None,
    ) -> MultiAgentRun:
        start = time.perf_counter()
        context_results = self.retrieval.search(
            prompt,
            document_ids=document_ids or [],
            top_k=top_k or self.settings.retrieval_top_k,
        )
        retrieved_context = [
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
        graph = self._build_graph()
        initial_state: MultiAgentState = {
            "user_prompt": prompt,
            "task_category": task_category,
            "retrieved_context": retrieved_context,
            "revision_count": 0,
            "revision_required": False,
            "agent_runs": [],
            "errors": [],
            "status": "started",
        }
        final_state = await graph.ainvoke(initial_state)
        if final_state.get("errors"):
            raise ShodhAIError("; ".join(final_state["errors"]), error_type="agent_workflow_failure")
        agent_runs = final_state.get("agent_runs", [])
        model_name = self.settings.ollama_model
        if agent_runs:
            model_name = (
                (agent_runs[-1].get("metadata_json") or {}).get("model")
                or model_name
            )
        return MultiAgentRun(
            response=final_state.get("final_response") or final_state.get("verification") or "",
            execution_time_seconds=time.perf_counter() - start,
            model_name=model_name,
            revision_attempts=final_state.get("revision_count", 0),
            retrieval_context=retrieved_context,
            agent_runs=agent_runs,
            metadata={
                "workflow": "LangGraph StateGraph",
                "max_revision_attempts": self.settings.max_revision_attempts,
                "status": final_state.get("status"),
            },
        )

    def _build_graph(self):
        try:
            from langgraph.graph import END, StateGraph
        except ImportError as exc:
            raise ShodhAIError(
                "LangGraph is not installed. Install backend requirements before running the multi-agent workflow.",
                error_type="langgraph_missing",
            ) from exc

        workflow = StateGraph(MultiAgentState)
        workflow.add_node("research", self._research_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("writer", self._writer_node)
        workflow.add_node("reviewer", self._reviewer_node)
        workflow.add_node("verifier", self._verifier_node)
        workflow.set_entry_point("research")
        workflow.add_edge("research", "planner")
        workflow.add_edge("planner", "writer")
        workflow.add_edge("writer", "reviewer")
        workflow.add_conditional_edges(
            "reviewer",
            self._next_after_review,
            {"writer": "writer", "verifier": "verifier"},
        )
        workflow.add_edge("verifier", END)
        return workflow.compile()

    async def _research_node(self, state: MultiAgentState) -> MultiAgentState:
        output = await self.research_agent.run(
            user_prompt=state["user_prompt"],
            task_category=state["task_category"],
            retrieved_context=state.get("retrieved_context", []),
        )
        state["research_notes"] = output.output
        self._append_agent_run(state, output, sequence=1)
        state["status"] = "research_completed"
        return state

    async def _planner_node(self, state: MultiAgentState) -> MultiAgentState:
        output = await self.planner_agent.run(
            user_prompt=state["user_prompt"],
            research_notes=state.get("research_notes", ""),
        )
        state["plan"] = output.output
        self._append_agent_run(state, output, sequence=2)
        state["status"] = "planning_completed"
        return state

    async def _writer_node(self, state: MultiAgentState) -> MultiAgentState:
        feedback = state.get("review") if state.get("revision_required") else None
        if feedback:
            state["revision_count"] = state.get("revision_count", 0) + 1
        output = await self.writer_agent.run(
            user_prompt=state["user_prompt"],
            research_notes=state.get("research_notes", ""),
            plan=state.get("plan", ""),
            review_feedback=feedback,
        )
        state["draft"] = output.output
        sequence = 3 + state.get("revision_count", 0) * 2
        self._append_agent_run(state, output, sequence=sequence)
        state["status"] = "writing_completed"
        return state

    async def _reviewer_node(self, state: MultiAgentState) -> MultiAgentState:
        output = await self.reviewer_agent.run(
            user_prompt=state["user_prompt"],
            draft=state.get("draft", ""),
            plan=state.get("plan", ""),
        )
        state["review"] = output.output
        state["revision_required"] = parse_revision_required(output.output)
        sequence = 4 + state.get("revision_count", 0) * 2
        self._append_agent_run(state, output, sequence=sequence)
        state["status"] = "review_completed"
        return state

    async def _verifier_node(self, state: MultiAgentState) -> MultiAgentState:
        output = await self.verifier_agent.run(
            user_prompt=state["user_prompt"],
            draft=state.get("draft", ""),
            review=state.get("review", ""),
            retrieved_context=state.get("retrieved_context", []),
        )
        state["verification"] = output.output
        state["final_response"] = output.output
        sequence = 5 + state.get("revision_count", 0) * 2
        self._append_agent_run(state, output, sequence=sequence)
        state["status"] = "completed"
        return state

    def _next_after_review(self, state: MultiAgentState) -> str:
        if (
            state.get("revision_required")
            and state.get("revision_count", 0) < self.settings.max_revision_attempts
        ):
            return "writer"
        return "verifier"

    @staticmethod
    def _append_agent_run(
        state: MultiAgentState, output: AgentOutput, *, sequence: int
    ) -> None:
        state.setdefault("agent_runs", []).append(
            {
                "agent_name": output.agent_name,
                "sequence": sequence,
                "status": "completed",
                "duration_seconds": round(output.duration_seconds, 3),
                "summary": output.summary,
                "output": output.output,
                "metadata_json": output.metadata,
            }
        )
