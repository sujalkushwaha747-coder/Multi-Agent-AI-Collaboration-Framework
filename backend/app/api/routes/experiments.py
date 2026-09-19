import logging

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session, experiment_service
from app.core.exceptions import http_bad_request, http_not_found
from app.database.session import SessionLocal
from app.schemas.experiment import (
    BenchmarkRunRequest,
    ExperimentCreate,
    ExperimentListItem,
    ExperimentRead,
    ExperimentRunOptions,
    RunComparisonRequest,
)
from app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/experiments", tags=["experiments"])
logger = logging.getLogger(__name__)


async def run_comparison_background(experiment_id: str) -> None:
    db = SessionLocal()
    service = ExperimentService()
    try:
        experiment = service.get(db, experiment_id)
        if not experiment:
            logger.error("Queued experiment not found", extra={"experiment_id": experiment_id})
            return
        await service.run_both(db, experiment)
    except Exception as exc:
        logger.exception("Background comparison failed", extra={"experiment_id": experiment_id})
        experiment = service.get(db, experiment_id)
        if experiment:
            experiment.status = "failed"
            experiment.error_message = str(exc)
            db.add(experiment)
            db.commit()
    finally:
        db.close()


@router.post("", response_model=ExperimentRead, status_code=201)
def create_experiment(
    payload: ExperimentCreate,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    return service.create(
        db,
        prompt=payload.prompt,
        task_category=payload.task_category,
        document_ids=payload.document_ids,
        reference_answer=payload.reference_answer,
    )


@router.post("/run-comparison", response_model=ExperimentRead, status_code=201)
async def create_and_run_comparison(
    payload: RunComparisonRequest,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.create(
        db,
        prompt=payload.prompt,
        task_category=payload.task_category,
        document_ids=payload.document_ids,
        reference_answer=payload.reference_answer,
    )
    return await service.run_both(db, experiment)


@router.post("/run-comparison-async", response_model=ExperimentRead, status_code=202)
async def create_and_queue_comparison(
    payload: RunComparisonRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.create(
        db,
        prompt=payload.prompt,
        task_category=payload.task_category,
        document_ids=payload.document_ids,
        reference_answer=payload.reference_answer,
    )
    experiment.status = "queued"
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    background_tasks.add_task(run_comparison_background, experiment.id)
    return experiment


@router.post("/benchmark-run", response_model=list[ExperimentRead], status_code=201)
async def run_benchmark(
    payload: BenchmarkRunRequest,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    prompts = payload.prompts
    if not prompts:
        from app.models.benchmark import BenchmarkPrompt

        seed_prompts = db.query(BenchmarkPrompt).order_by(BenchmarkPrompt.category).all()
        prompts = [
            ExperimentCreate(prompt=item.prompt, task_category=item.category)  # type: ignore[arg-type]
            for item in seed_prompts
        ]
    if not prompts:
        raise http_bad_request("No benchmark prompts are available.")

    results = []
    for item in prompts:
        experiment = service.create(
            db,
            prompt=item.prompt,
            task_category=item.task_category,
            document_ids=item.document_ids,
            reference_answer=item.reference_answer,
        )
        results.append(await service.run_both(db, experiment))
    return results


@router.get("", response_model=list[ExperimentListItem])
def list_experiments(
    search: str | None = None,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    return [service.to_list_item(item) for item in service.list(db, search=search)]


@router.get("/{experiment_id}", response_model=ExperimentRead)
def get_experiment(
    experiment_id: str,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.get(db, experiment_id)
    if not experiment:
        raise http_not_found("Experiment not found.")
    return experiment


@router.post("/{experiment_id}/run-single", response_model=ExperimentRead)
async def run_single(
    experiment_id: str,
    payload: ExperimentRunOptions | None = None,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.get(db, experiment_id)
    if not experiment:
        raise http_not_found("Experiment not found.")
    return await service.run_single(db, experiment, top_k=payload.top_k if payload else None)


@router.post("/{experiment_id}/run-multi", response_model=ExperimentRead)
async def run_multi(
    experiment_id: str,
    payload: ExperimentRunOptions | None = None,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.get(db, experiment_id)
    if not experiment:
        raise http_not_found("Experiment not found.")
    return await service.run_multi(db, experiment, top_k=payload.top_k if payload else None)


@router.post("/{experiment_id}/run-both", response_model=ExperimentRead)
async def run_both(
    experiment_id: str,
    payload: ExperimentRunOptions | None = None,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.get(db, experiment_id)
    if not experiment:
        raise http_not_found("Experiment not found.")
    return await service.run_both(db, experiment, top_k=payload.top_k if payload else None)


@router.delete("/{experiment_id}", status_code=204)
def delete_experiment(
    experiment_id: str,
    db: Session = Depends(db_session),
    service: ExperimentService = Depends(experiment_service),
):
    experiment = service.get(db, experiment_id)
    if not experiment:
        raise http_not_found("Experiment not found.")
    service.delete(db, experiment)
    return None
