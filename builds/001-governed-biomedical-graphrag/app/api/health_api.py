from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel

from app.config.settings import get_settings


class HealthResponse(BaseModel):
    status: str
    service: str
    build: str
    app_env: str
    pubmed_enabled: bool
    graph_validation_enabled: bool
    strict_safety_enabled: bool
    timestamp_utc: datetime


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()

    return HealthResponse(
        status="ok",
        service="governed-biomedical-graphrag",
        build="001-governed-biomedical-graphrag",
        app_env=settings.app_env,
        pubmed_enabled=settings.enable_pubmed,
        graph_validation_enabled=settings.enable_graph_validation,
        strict_safety_enabled=settings.enable_strict_safety,
        timestamp_utc=datetime.now(UTC),
    )
