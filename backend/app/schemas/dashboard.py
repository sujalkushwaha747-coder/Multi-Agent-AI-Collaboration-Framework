from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_experiments: int
    completed_experiments: int
    single_agent_average_score: float | None
    multi_agent_average_score: float | None
    average_single_execution_time: float | None
    average_multi_execution_time: float | None
    average_accuracy_single: float | None
    average_accuracy_multi: float | None
    average_quality_single: float | None
    average_quality_multi: float | None
    average_hallucination_single: float | None
    average_hallucination_multi: float | None
    average_completeness_single: float | None
    average_completeness_multi: float | None
    multi_agent_improvement_percentage: float | None


class DashboardMetricPoint(BaseModel):
    experiment_id: str
    created_at: str
    task_category: str
    accuracy_single: float | None
    accuracy_multi: float | None
    quality_single: float | None
    quality_multi: float | None
    completeness_single: float | None
    completeness_multi: float | None
    hallucination_single: float | None
    hallucination_multi: float | None
    execution_time_single: float | None
    execution_time_multi: float | None
    overall_single: float | None
    overall_multi: float | None

