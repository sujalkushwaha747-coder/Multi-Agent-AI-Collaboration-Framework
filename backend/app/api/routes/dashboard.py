from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import dashboard_service, db_session
from app.schemas.dashboard import DashboardMetricPoint, DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(
    db: Session = Depends(db_session),
    service: DashboardService = Depends(dashboard_service),
):
    return service.summary(db)


@router.get("/metrics", response_model=list[DashboardMetricPoint])
def metrics(
    db: Session = Depends(db_session),
    service: DashboardService = Depends(dashboard_service),
):
    return service.metrics(db)

