from __future__ import annotations

from datetime import datetime
from typing import Literal

import sqlalchemy as sa
from fastapi import APIRouter
from pydantic import BaseModel

from src.core.config import settings
from src.core.database import engine
from src.core.redis_client import redis_client

router = APIRouter()


class ComponentStatus(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    latency_ms: float | None = None
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    version: str
    database: ComponentStatus
    redis: ComponentStatus


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    db_status = await _check_database()
    redis_status = await _check_redis()

    overall: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    if db_status.status == "unhealthy" or redis_status.status == "unhealthy":
        overall = "unhealthy"
    elif db_status.status == "degraded" or redis_status.status == "degraded":
        overall = "degraded"

    return HealthResponse(
        status=overall,
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database=db_status,
        redis=redis_status,
    )


async def _check_database() -> ComponentStatus:
    import time

    start = time.monotonic()
    try:
        async with engine.begin() as conn:
            await conn.execute(sa.text("SELECT 1"))
        latency = (time.monotonic() - start) * 1000
        return ComponentStatus(
            status="healthy" if latency < 100 else "degraded",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        return ComponentStatus(status="unhealthy", detail=str(e))


async def _check_redis() -> ComponentStatus:
    import time

    start = time.monotonic()
    try:
        await redis_client.ping()
        latency = (time.monotonic() - start) * 1000
        return ComponentStatus(
            status="healthy" if latency < 50 else "degraded",
            latency_ms=round(latency, 2),
        )
    except Exception as e:
        return ComponentStatus(status="unhealthy", detail=str(e))

