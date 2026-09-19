from app.evaluation.evaluator import EvaluationEngine
from app.evaluation.scoring import (
    metric_winner,
    normalized_overall,
    safe_improvement_percentage,
)


def test_metric_winner_handles_lower_is_better() -> None:
    assert metric_winner(20, 10, higher_is_better=False) == "Multi-Agent"
    assert metric_winner(10, 20, higher_is_better=False) == "Single-Agent"


def test_safe_improvement_avoids_zero_denominator() -> None:
    assert safe_improvement_percentage(0, 10, higher_is_better=True) is None
    assert safe_improvement_percentage(50, 75, higher_is_better=True) == 50
    assert safe_improvement_percentage(20, 10, higher_is_better=False) == 50


def test_overall_normalizes_inverse_metrics() -> None:
    score = normalized_overall(
        accuracy=80,
        quality=80,
        completeness=80,
        hallucination=10,
        execution_time=2,
        max_execution_time=4,
        weights={
            "accuracy": 0.25,
            "quality": 0.25,
            "completeness": 0.20,
            "hallucination": 0.20,
            "execution_time": 0.10,
        },
    )
    assert score is not None
    assert 75 <= score <= 90


def test_evaluator_labels_estimated_metrics_without_reference() -> None:
    result = EvaluationEngine().evaluate(
        prompt="Explain RAG and its advantages.",
        single_response="RAG retrieves context and improves grounded answers.",
        multi_response="Retrieval-Augmented Generation retrieves evidence before generation and can improve grounding.",
        single_time=1.2,
        multi_time=2.0,
    )
    assert result["metrics"]
    assert result["methodology"]["estimated_metrics_present"] is True
    assert result["winner"] in {"Single-Agent", "Multi-Agent", "Tie"}

