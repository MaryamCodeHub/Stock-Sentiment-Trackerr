from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Float, Index, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Price(Base):
    __tablename__ = "prices"

    timestamp: Mapped[datetime] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="alpha_vantage")

    __table_args__ = (Index("ix_prices_symbol_timestamp", "symbol", "timestamp"),)


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    timestamp: Mapped[datetime] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    score: Mapped[float] = mapped_column(Float)
    label: Mapped[str] = mapped_column(String(20))
    compound: Mapped[float] = mapped_column(Float, default=0.0)
    article_count: Mapped[int] = mapped_column(BigInteger, default=0)
    source: Mapped[str] = mapped_column(String(50))

    __table_args__ = (Index("ix_sentiment_symbol_timestamp", "symbol", "timestamp"),)


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    published_at: Mapped[datetime] = mapped_column(index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(2000))
    url: Mapped[str] = mapped_column(String(1000))
    source: Mapped[str] = mapped_column(String(100))
    sentiment_label: Mapped[str | None] = mapped_column(String(20))
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    image_url: Mapped[str | None] = mapped_column(String(1000))

    __table_args__ = (
        UniqueConstraint("url", name="uq_news_url"),
        Index("ix_news_symbol_published", "symbol", "published_at"),
    )

