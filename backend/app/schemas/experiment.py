from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import TaskCategory


class ExperimentCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    task_category: TaskCategory = "general"
    document_ids: list[str] = Field(default_factory=list)
    reference_answer: str | None = Field(default=None, max_length=20000)

    @field_validator("prompt")
    @classmethod
    def prompt_must_have_content(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Prompt cannot be empty.")
        return cleaned


class RunComparisonRequest(ExperimentCreate):
    pass


class ExperimentRunOptions(BaseModel):
    top_k: int | None = Field(default=None, ge=1, le=12)


class AgentRunRead(BaseModel):
    id: str
    agent_name: str
    sequence: int
    status: str
    duration_seconds: float | None
    summary: str | None
    output: str | None
    metadata_json: dict[str, Any]
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SingleAgentResultRead(BaseModel):
    id: str
    response: str
    status: str
    execution_time_seconds: float | None
    model_name: str | None
    retrieval_context: list[dict[str, Any]]
    metadata_json: dict[str, Any]
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MultiAgentResultRead(BaseModel):
    id: str
    response: str
    status: str
    execution_time_seconds: float | None
    model_name: str | None
    revision_attempts: int
    retrieval_context: list[dict[str, Any]]
    metadata_json: dict[str, Any]
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class EvaluationMetricRead(BaseModel):
    metric: str
    single_agent: float | None
    multi_agent: float | None
    difference: float | None
    better_architecture: Literal["Single-Agent", "Multi-Agent", "Tie", "Not evaluated"]
    higher_is_better: bool
    methodology: str
    estimated: bool = False


class EvaluationResultRead(BaseModel):
    id: str
    status: str
    accuracy_single: float | None
    accuracy_multi: float | None
    quality_single: float | None
    quality_multi: float | None
    hallucination_single: float | None
    hallucination_multi: float | None
    completeness_single: float | None
    completeness_multi: float | None
    overall_single: float | None
    overall_multi: float | None
    winner: str | None
    methodology: dict[str, Any]
    metrics: list[EvaluationMetricRead]
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ExperimentRead(BaseModel):
    id: str
    prompt: str
    task_category: str
    reference_answer: str | None
    document_ids: list[str]
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    single_result: SingleAgentResultRead | None
    multi_result: MultiAgentResultRead | None
    evaluation: EvaluationResultRead | None
    agent_runs: list[AgentRunRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ExperimentListItem(BaseModel):
    id: str
    prompt: str
    task_category: str
    status: str
    created_at: datetime
    single_score: float | None = None
    multi_score: float | None = None
    winner: str | None = None
    single_execution_time: float | None = None
    multi_execution_time: float | None = None


class BenchmarkRunRequest(BaseModel):
    prompts: list[ExperimentCreate] = Field(default_factory=list)
    use_seed_prompts: bool = True

