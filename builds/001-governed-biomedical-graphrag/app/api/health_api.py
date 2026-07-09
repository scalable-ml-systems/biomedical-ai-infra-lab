from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    build: str
    timestamp_utc: datetime


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="governed-biomedical-graphrag",
        build="001-governed-biomedical-graphrag",
        timestamp_utc=datetime.now(UTC),
    )
