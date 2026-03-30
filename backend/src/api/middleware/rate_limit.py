from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.redis_client import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 60) -> None:
        super().__init__(app)
        self.limit = limit

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in ("/api/v1/health", "/metrics"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"sst:ratelimit:{client_ip}"
        now = time.time()
        window = 60

        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - window)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window * 2)
        results = await pipe.execute()

        request_count = results[2]
        if request_count > self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": self.limit,
                    "window": "60 seconds",
                    "retry_after": window,
                },
                headers={
                    "X-RateLimit-Limit": str(self.limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(window),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.limit - request_count))
        return response

