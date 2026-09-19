from statistics import mean

from sqlalchemy.orm import Session, selectinload

from app.evaluation.scoring import safe_improvement_percentage
from app.models.experiment import Experiment


class DashboardService:
    def summary(self, db: Session) -> dict:
        experiments = (
            db.query(Experiment)
            .options(
                selectinload(Experiment.single_result),
                selectinload(Experiment.multi_result),
                selectinload(Experiment.evaluation),
            )
            .all()
        )
        completed = [item for item in experiments if item.evaluation and item.evaluation.status == "completed"]

        def avg(values: list[float | None]) -> float | None:
            present = [value for value in values if value is not None]
            return round(mean(present), 2) if present else None

        single_overall = avg([item.evaluation.overall_single for item in completed])
        multi_overall = avg([item.evaluation.overall_multi for item in completed])

        return {
            "total_experiments": len(experiments),
            "completed_experiments": len(completed),
            "single_agent_average_score": single_overall,
            "multi_agent_average_score": multi_overall,
            "average_single_execution_time": avg(
                [item.single_result.execution_time_seconds if item.single_result else None for item in completed]
            ),
            "average_multi_execution_time": avg(
                [item.multi_result.execution_time_seconds if item.multi_result else None for item in completed]
            ),
            "average_accuracy_single": avg([item.evaluation.accuracy_single for item in completed]),
            "average_accuracy_multi": avg([item.evaluation.accuracy_multi for item in completed]),
            "average_quality_single": avg([item.evaluation.quality_single for item in completed]),
            "average_quality_multi": avg([item.evaluation.quality_multi for item in completed]),
            "average_hallucination_single": avg([item.evaluation.hallucination_single for item in completed]),
            "average_hallucination_multi": avg([item.evaluation.hallucination_multi for item in completed]),
            "average_completeness_single": avg([item.evaluation.completeness_single for item in completed]),
            "average_completeness_multi": avg([item.evaluation.completeness_multi for item in completed]),
            "multi_agent_improvement_percentage": safe_improvement_percentage(
                single_overall, multi_overall, higher_is_better=True
            ),
        }

    def metrics(self, db: Session) -> list[dict]:
        experiments = (
            db.query(Experiment)
            .options(
                selectinload(Experiment.single_result),
                selectinload(Experiment.multi_result),
                selectinload(Experiment.evaluation),
            )
            .order_by(Experiment.created_at.asc())
            .all()
        )
        points = []
        for experiment in experiments:
            evaluation = experiment.evaluation
            if not evaluation:
                continue
            points.append(
                {
                    "experiment_id": experiment.id,
                    "created_at": experiment.created_at.isoformat(),
                    "task_category": experiment.task_category,
                    "accuracy_single": evaluation.accuracy_single,
                    "accuracy_multi": evaluation.accuracy_multi,
                    "quality_single": evaluation.quality_single,
                    "quality_multi": evaluation.quality_multi,
                    "completeness_single": evaluation.completeness_single,
                    "completeness_multi": evaluation.completeness_multi,
                    "hallucination_single": evaluation.hallucination_single,
                    "hallucination_multi": evaluation.hallucination_multi,
                    "execution_time_single": experiment.single_result.execution_time_seconds
                    if experiment.single_result
                    else None,
                    "execution_time_multi": experiment.multi_result.execution_time_seconds
                    if experiment.multi_result
                    else None,
                    "overall_single": evaluation.overall_single,
                    "overall_multi": evaluation.overall_multi,
                }
            )
        return points

