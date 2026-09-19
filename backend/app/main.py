from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import benchmarks, dashboard, documents, experiments, health
from app.core.config import get_settings
from app.core.exceptions import ShodhAIError
from app.core.logging import RequestLoggingMiddleware, configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="ShodhAI: A Comparative Framework for Evaluating Single-Agent and Multi-Agent Large Language Model Systems",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_origins,
    allow_origin_regex=settings.resolved_cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(experiments.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(benchmarks.router, prefix=settings.api_prefix)


@app.on_event("startup")
def ensure_runtime_dirs() -> None:
    settings.resolved_upload_dir.mkdir(parents=True, exist_ok=True)
    settings.resolved_faiss_index_path.mkdir(parents=True, exist_ok=True)


@app.exception_handler(ShodhAIError)
async def shodhai_error_handler(_: Request, exc: ShodhAIError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message, "error_type": exc.error_type},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed.",
            "errors": exc.errors(),
        },
    )
