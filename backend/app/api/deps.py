from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.dashboard_service import DashboardService
from app.services.document_service import DocumentService
from app.services.experiment_service import ExperimentService


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def experiment_service() -> ExperimentService:
    return ExperimentService()


def document_service() -> DocumentService:
    return DocumentService()


def dashboard_service() -> DashboardService:
    return DashboardService()

