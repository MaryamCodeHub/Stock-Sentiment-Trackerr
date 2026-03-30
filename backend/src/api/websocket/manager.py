from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket

from src.core.redis_client import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._subscriptions: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, symbol: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._subscriptions[symbol].add(websocket)

    async def disconnect(self, websocket: WebSocket, symbol: str) -> None:
        async with self._lock:
            self._subscriptions[symbol].discard(websocket)
            if not self._subscriptions[symbol]:
                del self._subscriptions[symbol]

    async def broadcast(self, symbol: str, data: dict) -> None:
        message = json.dumps(data)
        connections = self._subscriptions.get(symbol, set()).copy()
        dead: set[WebSocket] = set()
        for ws in connections:
            try:
                await ws.send_text(message)
            except Exception:
                dead.add(ws)
        if dead:
            async with self._lock:
                self._subscriptions[symbol] -= dead

    async def start_redis_listener(self) -> None:
        pubsub = redis_client.pubsub()
        await pubsub.psubscribe("prices:*")
        async for message in pubsub.listen():
            if message.get("type") != "pmessage":
                continue
            try:
                channel = message["channel"]
                if isinstance(channel, bytes):
                    channel = channel.decode()
                symbol = str(channel).split(":")[1]
                payload = message["data"]
                if isinstance(payload, bytes):
                    payload = payload.decode()
                data = json.loads(payload)
                await self.broadcast(symbol, data)
            except Exception as e:
                logger.error("Redis pub/sub error", extra={"error": str(e)})


manager = ConnectionManager()

