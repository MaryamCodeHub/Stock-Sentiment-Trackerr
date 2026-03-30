from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.api.websocket.manager import manager

websocket_router = APIRouter()


@websocket_router.websocket("/ws/prices/{symbol}")
async def prices_ws(websocket: WebSocket, symbol: str) -> None:
    symbol = symbol.upper()
    await manager.connect(websocket, symbol)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(websocket, symbol)

