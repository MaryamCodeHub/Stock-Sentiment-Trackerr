from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OHLCVResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    change_pct: float = Field(description="Percentage change from open to close")


class SentimentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    score: float = Field(ge=0.0, le=1.0)
    label: Literal["positive", "neutral", "negative"]
    compound: float = Field(ge=-1.0, le=1.0)
    article_count: int
    timestamp: datetime
    trend_24h: float | None = None


class NewsArticleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    published_at: datetime
    symbol: str
    title: str
    description: str | None
    url: str
    source: str
    sentiment_label: Literal["positive", "neutral", "negative"] | None
    sentiment_score: float | None
    image_url: str | None


class TopMoverResponse(BaseModel):
    symbol: str
    name: str
    price: float
    change_pct: float
    volume: float
    sentiment_score: float | None
    sentiment_label: str | None
    sparkline: list[float]


class KPIResponse(BaseModel):
    total_market_cap: float
    total_volume_24h: float
    fear_greed_index: int
    fear_greed_label: str
    top_gainer_symbol: str
    top_gainer_pct: float
    top_loser_symbol: str
    top_loser_pct: float
    overall_sentiment_score: float
    updated_at: datetime


class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    has_next: bool
