from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.schemas import OHLCVResponse

router = APIRouter()


@router.get("/{symbol}", response_model=list[OHLCVResponse])
async def get_prices(
    symbol: str,
    interval: Annotated[str, Query(pattern="^(1D|1W|1M|3M|1Y|ALL)$")] = "1D",
    db: AsyncSession = Depends(get_db),
) -> list[OHLCVResponse]:
    symbol = symbol.upper()
    _ = (db, interval, datetime.utcnow() - timedelta(days=1))
    raise HTTPException(status_code=501, detail="Prices endpoint scaffolded (not implemented yet)")

