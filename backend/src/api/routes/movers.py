from __future__ import annotations

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def get_top_movers():
    raise HTTPException(status_code=501, detail="Movers endpoint scaffolded (not implemented yet)")

