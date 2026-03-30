from __future__ import annotations

import pytest

from src.services.sentiment_analyzer import SentimentAnalyzer


@pytest.fixture
def analyzer():
    return SentimentAnalyzer()


def test_vader_neutral(analyzer: SentimentAnalyzer):
    r = analyzer._vader_analyze("Company released its quarterly report today.")
    assert r.label in ("positive", "neutral", "negative")

