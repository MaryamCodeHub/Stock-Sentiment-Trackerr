from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_returns_200(client: AsyncClient):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] in ("healthy", "degraded", "unhealthy")

