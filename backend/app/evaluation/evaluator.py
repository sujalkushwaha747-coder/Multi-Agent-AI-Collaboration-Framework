from app.core.config import Settings, get_settings
from app.evaluation.scoring import (
    accuracy_score,
    completeness_score,
    hallucination_rate,
    metric_winner,
    normalized_overall,
    quality_score,
    safe_improvement_percentage,
)


class EvaluationEngine:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    def evaluate(
        self,
        *,
        prompt: str,
        single_response: str,
        multi_response: str,
        single_time: float | None,
        multi_time: float | None,
        reference_answer: str | None = None,
        evidence_chunks: list[str] | None = None,
    ) -> dict:
        evidence_chunks = evidence_chunks or []

        single_accuracy = accuracy_score(single_response, reference_answer, evidence_chunks)
        multi_accuracy = accuracy_score(multi_response, reference_answer, evidence_chunks)
        single_quality = quality_score(single_response)
        multi_quality = quality_score(multi_response)
        single_hallucination = hallucination_rate(single_response, evidence_chunks)
        multi_hallucination = hallucination_rate(multi_response, evidence_chunks)
        single_completeness = completeness_score(prompt, single_response)
        multi_completeness = completeness_score(prompt, multi_response)

        max_time = max([t for t in [single_time, multi_time] if t is not None], default=None)
        single_overall = normalized_overall(
            accuracy=single_accuracy.score,
            quality=single_quality.score,
            completeness=single_completeness.score,
            hallucination=single_hallucination.score,
            execution_time=single_time,
            max_execution_time=max_time,
            weights=self.settings.overall_weights,
        )
        multi_overall = normalized_overall(
            accuracy=multi_accuracy.score,
            quality=multi_quality.score,
            completeness=multi_completeness.score,
            hallucination=multi_hallucination.score,
            execution_time=multi_time,
            max_execution_time=max_time,
            weights=self.settings.overall_weights,
        )

        metrics = [
            self._metric("Accuracy", single_accuracy, multi_accuracy, True),
            self._metric("Response Quality", single_quality, multi_quality, True),
            self._metric("Hallucination Rate", single_hallucination, multi_hallucination, False),
            self._metric("Completeness", single_completeness, multi_completeness, True),
            {
                "metric": "Execution Time",
                "single_agent": round(single_time, 3) if single_time is not None else None,
                "multi_agent": round(multi_time, 3) if multi_time is not None else None,
                "difference": round((multi_time or 0) - (single_time or 0), 3)
                if single_time is not None and multi_time is not None
                else None,
                "better_architecture": metric_winner(single_time, multi_time, higher_is_better=False),
                "higher_is_better": False,
                "methodology": "High-resolution backend wall-clock execution time in seconds.",
                "estimated": False,
            },
            {
                "metric": "Overall Comparison",
                "single_agent": single_overall,
                "multi_agent": multi_overall,
                "difference": round((multi_overall or 0) - (single_overall or 0), 2)
                if single_overall is not None and multi_overall is not None
                else None,
                "better_architecture": metric_winner(single_overall, multi_overall, higher_is_better=True),
                "higher_is_better": True,
                "methodology": "Weighted normalized score. Hallucination and time are inverted before weighting.",
                "estimated": True,
            },
        ]
        winner = metric_winner(single_overall, multi_overall, higher_is_better=True)
        if winner == "Not evaluated":
            winner = None

        return {
            "accuracy_single": single_accuracy.score,
            "accuracy_multi": multi_accuracy.score,
            "quality_single": single_quality.score,
            "quality_multi": multi_quality.score,
            "hallucination_single": single_hallucination.score,
            "hallucination_multi": multi_hallucination.score,
            "completeness_single": single_completeness.score,
            "completeness_multi": multi_completeness.score,
            "overall_single": single_overall,
            "overall_multi": multi_overall,
            "winner": winner,
            "metrics": metrics,
            "methodology": {
                "accuracy": single_accuracy.methodology
                if single_accuracy.methodology == multi_accuracy.methodology
                else {
                    "single": single_accuracy.methodology,
                    "multi": multi_accuracy.methodology,
                },
                "quality": single_quality.methodology,
                "hallucination": single_hallucination.methodology
                if single_hallucination.methodology == multi_hallucination.methodology
                else {
                    "single": single_hallucination.methodology,
                    "multi": multi_hallucination.methodology,
                },
                "completeness": single_completeness.methodology,
                "overall_weights": self.settings.overall_weights,
                "estimated_metrics_present": any(metric["estimated"] for metric in metrics),
            },
        }

    @staticmethod
    def _metric(name: str, single, multi, higher_is_better: bool) -> dict:
        return {
            "metric": name,
            "single_agent": single.score,
            "multi_agent": multi.score,
            "difference": round(multi.score - single.score, 2),
            "better_architecture": metric_winner(
                single.score, multi.score, higher_is_better=higher_is_better
            ),
            "higher_is_better": higher_is_better,
            "methodology": single.methodology
            if single.methodology == multi.methodology
            else f"Single: {single.methodology} Multi: {multi.methodology}",
            "estimated": single.estimated or multi.estimated,
            "improvement_percentage": safe_improvement_percentage(
                single.score, multi.score, higher_is_better=higher_is_better
            ),
        }

