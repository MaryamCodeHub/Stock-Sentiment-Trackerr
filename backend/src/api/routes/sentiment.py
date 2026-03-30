from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{symbol}")
async def get_sentiment(symbol: str):
    _ = symbol
    raise HTTPException(status_code=501, detail="Sentiment endpoint scaffolded (not implemented yet)")

