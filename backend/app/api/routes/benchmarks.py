from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.models.benchmark import BenchmarkPrompt

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.get("/prompts")
def list_benchmark_prompts(db: Session = Depends(db_session)) -> list[dict]:
    prompts = db.query(BenchmarkPrompt).order_by(BenchmarkPrompt.category).all()
    return [
        {
            "id": item.id,
            "category": item.category,
            "prompt": item.prompt,
            "source": item.source,
        }
        for item in prompts
    ]

