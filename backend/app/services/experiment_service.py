from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings, get_settings
from app.evaluation.evaluator import EvaluationEngine
from app.models.experiment import (
    AgentRun,
    EvaluationResult,
    Experiment,
    MultiAgentResult,
    SingleAgentResult,
)
from app.schemas.common import TaskCategory
from app.services.multi_agent import MultiAgentService
from app.services.single_agent import SingleAgentService
from app.services.task_classifier import classify_task

logger = logging.getLogger(__name__)


class ExperimentService:
    def __init__(
        self,
        settings: Settings | None = None,
        single_agent: SingleAgentService | None = None,
        multi_agent: MultiAgentService | None = None,
        evaluator: EvaluationEngine | None = None,
    ):
        self.settings = settings or get_settings()
        self.single_agent = single_agent or SingleAgentService(settings=self.settings)
        self.multi_agent = multi_agent or MultiAgentService(settings=self.settings)
        self.evaluator = evaluator or EvaluationEngine(self.settings)

    def create(
        self,
        db: Session,
        *,
        prompt: str,
        task_category: TaskCategory = "general",
        document_ids: list[str] | None = None,
        reference_answer: str | None = None,
    ) -> Experiment:
        category = classify_task(prompt, task_category)
        experiment = Experiment(
            prompt=prompt,
            task_category=category,
            document_ids=document_ids or [],
            reference_answer=reference_answer,
            status="created",
        )
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment

    def get(self, db: Session, experiment_id: str) -> Experiment | None:
        return (
            db.query(Experiment)
            .options(
                selectinload(Experiment.single_result),
                selectinload(Experiment.multi_result),
                selectinload(Experiment.evaluation),
                selectinload(Experiment.agent_runs),
            )
            .filter(Experiment.id == experiment_id)
            .one_or_none()
        )

    def list(self, db: Session, *, search: str | None = None) -> list[Experiment]:
        query = (
            db.query(Experiment)
            .options(
                selectinload(Experiment.single_result),
                selectinload(Experiment.multi_result),
                selectinload(Experiment.evaluation),
            )
            .order_by(Experiment.created_at.desc())
        )
        if search:
            query = query.filter(Experiment.prompt.ilike(f"%{search}%"))
        return query.all()

    def delete(self, db: Session, experiment: Experiment) -> None:
        db.delete(experiment)
        db.commit()

    async def run_single(
        self, db: Session, experiment: Experiment, *, top_k: int | None = None
    ) -> Experiment:
        experiment.status = "running_single"
        db.add(experiment)
        db.commit()
        try:
            run = await self.single_agent.run(
                prompt=experiment.prompt,
                task_category=experiment.task_category,
                document_ids=experiment.document_ids,
                top_k=top_k,
            )
            self._replace_single_result(
                db,
                experiment,
                SingleAgentResult(
                    experiment_id=experiment.id,
                    response=run.response,
                    status="completed",
                    execution_time_seconds=run.execution_time_seconds,
                    model_name=run.model_name,
                    retrieval_context=run.retrieval_context,
                    metadata_json=run.metadata,
                ),
            )
        except Exception as exc:
            logger.exception(
                "Single-agent run failed",
                extra={"experiment_id": experiment.id, "error_type": type(exc).__name__},
            )
            self._replace_single_result(
                db,
                experiment,
                SingleAgentResult(
                    experiment_id=experiment.id,
                    response="",
                    status="failed",
                    error_message=str(exc),
                    metadata_json={"error_type": type(exc).__name__},
                ),
            )
        experiment.status = "single_completed"
        db.add(experiment)
        db.commit()
        return self.get(db, experiment.id) or experiment

    async def run_multi(
        self, db: Session, experiment: Experiment, *, top_k: int | None = None
    ) -> Experiment:
        experiment.status = "running_multi"
        db.add(experiment)
        db.commit()
        try:
            run = await self.multi_agent.run(
                prompt=experiment.prompt,
                task_category=experiment.task_category,
                document_ids=experiment.document_ids,
                top_k=top_k,
            )
            self._replace_multi_result(
                db,
                experiment,
                MultiAgentResult(
                    experiment_id=experiment.id,
                    response=run.response,
                    status="completed",
                    execution_time_seconds=run.execution_time_seconds,
                    model_name=run.model_name,
                    revision_attempts=run.revision_attempts,
                    retrieval_context=run.retrieval_context,
                    metadata_json=run.metadata,
                ),
            )
            self._replace_agent_runs(db, experiment, run.agent_runs)
        except Exception as exc:
            logger.exception(
                "Multi-agent run failed",
                extra={"experiment_id": experiment.id, "error_type": type(exc).__name__},
            )
            self._replace_multi_result(
                db,
                experiment,
                MultiAgentResult(
                    experiment_id=experiment.id,
                    response="",
                    status="failed",
                    error_message=str(exc),
                    metadata_json={"error_type": type(exc).__name__},
                ),
            )
        experiment.status = "multi_completed"
        db.add(experiment)
        db.commit()
        return self.get(db, experiment.id) or experiment

    async def run_both(
        self, db: Session, experiment: Experiment, *, top_k: int | None = None
    ) -> Experiment:
        experiment.status = "running"
        db.add(experiment)
        db.commit()
        experiment = await self.run_single(db, experiment, top_k=top_k)
        experiment = await self.run_multi(db, experiment, top_k=top_k)
        experiment = self.evaluate(db, experiment)
        return experiment

    def evaluate(self, db: Session, experiment: Experiment) -> Experiment:
        single = experiment.single_result
        multi = experiment.multi_result
        if not single or not multi or single.status != "completed" or multi.status != "completed":
            self._replace_evaluation(
                db,
                experiment,
                EvaluationResult(
                    experiment_id=experiment.id,
                    status="partial",
                    methodology={
                        "note": "Evaluation was not computed because one or both architectures failed."
                    },
                    metrics=[],
                    error_message="Both architectures must complete before comparison.",
                ),
            )
            experiment.status = "partial"
            db.add(experiment)
            db.commit()
            return self.get(db, experiment.id) or experiment

        evidence_chunks = [
            item.get("text", "")
            for item in [*(single.retrieval_context or []), *(multi.retrieval_context or [])]
        ]
        result = self.evaluator.evaluate(
            prompt=experiment.prompt,
            single_response=single.response,
            multi_response=multi.response,
            single_time=single.execution_time_seconds,
            multi_time=multi.execution_time_seconds,
            reference_answer=experiment.reference_answer,
            evidence_chunks=evidence_chunks,
        )
        self._replace_evaluation(
            db,
            experiment,
            EvaluationResult(
                experiment_id=experiment.id,
                status="completed",
                **result,
            ),
        )
        experiment.status = "completed"
        db.add(experiment)
        db.commit()
        return self.get(db, experiment.id) or experiment

    @staticmethod
    def to_list_item(experiment: Experiment) -> dict[str, Any]:
        return {
            "id": experiment.id,
            "prompt": experiment.prompt,
            "task_category": experiment.task_category,
            "status": experiment.status,
            "created_at": experiment.created_at,
            "single_score": experiment.evaluation.overall_single if experiment.evaluation else None,
            "multi_score": experiment.evaluation.overall_multi if experiment.evaluation else None,
            "winner": experiment.evaluation.winner if experiment.evaluation else None,
            "single_execution_time": experiment.single_result.execution_time_seconds
            if experiment.single_result
            else None,
            "multi_execution_time": experiment.multi_result.execution_time_seconds
            if experiment.multi_result
            else None,
        }

    @staticmethod
    def _replace_single_result(
        db: Session, experiment: Experiment, result: SingleAgentResult
    ) -> None:
        if experiment.single_result:
            db.delete(experiment.single_result)
            db.flush()
        db.add(result)
        db.commit()
        db.refresh(experiment)

    @staticmethod
    def _replace_multi_result(
        db: Session, experiment: Experiment, result: MultiAgentResult
    ) -> None:
        if experiment.multi_result:
            db.delete(experiment.multi_result)
            db.flush()
        db.add(result)
        db.commit()
        db.refresh(experiment)

    @staticmethod
    def _replace_evaluation(
        db: Session, experiment: Experiment, result: EvaluationResult
    ) -> None:
        if experiment.evaluation:
            db.delete(experiment.evaluation)
            db.flush()
        db.add(result)
        db.commit()
        db.refresh(experiment)

    @staticmethod
    def _replace_agent_runs(
        db: Session, experiment: Experiment, runs: list[dict[str, Any]]
    ) -> None:
        for existing in list(experiment.agent_runs):
            db.delete(existing)
        db.flush()
        for run in runs:
            db.add(AgentRun(experiment_id=experiment.id, **run))
        db.commit()
        db.refresh(experiment)
