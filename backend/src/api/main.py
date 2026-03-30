from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy as sa
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from src.api.routes import health
from src.api.websocket.manager import manager
from src.api.websocket.handlers import websocket_router
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.routes import movers, news, prices, sentiment
from src.core.config import settings
from src.core.database import engine
from src.core.logging import configure_logging
from src.core.redis_client import redis_client

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    await logger.ainfo("Starting Stock Sentiment Tracker")

    # During first container boot (e.g., slow/initial DB pull), allow
    # the API process to start even if dependencies are temporarily unavailable.
    # Health checks will report degraded/unhealthy until they recover.
    try:
        async with engine.begin() as conn:
            await conn.execute(sa.text("SELECT 1"))
        await logger.ainfo("Database connection established")
    except Exception as e:
        await logger.awarning(
            "Database connection failed during startup",
            extra={"error": str(e)},
        )

    redis_available = False
    try:
        await redis_client.ping()
        redis_available = True
        await logger.ainfo("Redis connection established")
    except Exception as e:
        await logger.awarning(
            "Redis connection failed during startup",
            extra={"error": str(e)},
        )

    redis_listener_task: asyncio.Task[None] | None = None
    if redis_available:
        redis_listener_task = asyncio.create_task(manager.start_redis_listener())
        await logger.ainfo("WebSocket redis listener started")

    yield

    if redis_listener_task is not None:
        redis_listener_task.cancel()
        try:
            await redis_listener_task
        except asyncio.CancelledError:
            pass

    await engine.dispose()
    try:
        await redis_client.aclose()
    except Exception:
        pass
    await logger.ainfo("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url="/api/redoc" if not settings.is_production else None,
        openapi_url="/api/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    app.add_middleware(RateLimitMiddleware, limit=settings.rate_limit_per_minute)

    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(prices.router, prefix="/api/v1/prices", tags=["Prices"])
    app.include_router(sentiment.router, prefix="/api/v1/sentiment", tags=["Sentiment"])
    app.include_router(news.router, prefix="/api/v1/news", tags=["News"])
    app.include_router(movers.router, prefix="/api/v1/movers", tags=["Movers"])
    app.include_router(websocket_router)

    if settings.prometheus_enabled:
        app.mount("/metrics", make_asgi_app())

    return app


app = create_app()

