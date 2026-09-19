from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.core.config import get_settings
from app.services.llm_service import OllamaLLMService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health(db: Session = Depends(db_session)) -> dict:
    database = {"available": False}
    try:
        db.execute(text("SELECT 1"))
        database = {"available": True}
    except Exception as exc:
        database = {"available": False, "error": str(exc)}

    settings = get_settings()
    llm = await OllamaLLMService(settings).health_check()
    return {
        "status": "ok" if database["available"] else "degraded",
        "app": settings.app_name,
        "environment": settings.app_env,
        "database": database,
        "llm": llm,
        "groq": llm.get("groq"),
        "ollama": llm.get("ollama"),
    }
