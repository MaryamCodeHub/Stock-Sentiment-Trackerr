from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{symbol}")
async def get_news(symbol: str):
    _ = symbol
    raise HTTPException(status_code=501, detail="News endpoint scaffolded (not implemented yet)")

