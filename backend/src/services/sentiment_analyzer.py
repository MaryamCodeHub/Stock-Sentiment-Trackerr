from __future__ import annotations

import logging
from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    label: str
    score: float
    compound: float


class SentimentAnalyzer:
    def __init__(self) -> None:
        self._finbert_loaded = False
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForSequenceClassification | None = None
        self._vader = SentimentIntensityAnalyzer()
        self._device = "cuda" if settings.use_gpu and torch.cuda.is_available() else "cpu"

    def load_finbert(self) -> None:
        if self._finbert_loaded:
            return
        logger.info("Loading FinBERT model...", extra={"model": settings.finbert_model_path})
        self._tokenizer = AutoTokenizer.from_pretrained(settings.finbert_model_path)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            settings.finbert_model_path
        ).to(self._device)
        self._model.eval()
        self._finbert_loaded = True

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        if not texts:
            return []
        if not self._finbert_loaded:
            self.load_finbert()

        results: list[SentimentResult] = []
        batch_size = settings.ml_batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                results.extend(self._finbert_batch(batch))
            except Exception:
                for t in batch:
                    results.append(self._vader_analyze(t))
        return results

    def _finbert_batch(self, texts: list[str]) -> list[SentimentResult]:
        assert self._tokenizer is not None
        assert self._model is not None

        inputs = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self._device)

        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)

        label_names = ["positive", "negative", "neutral"]
        out: list[SentimentResult] = []
        for row in probs:
            idx = int(row.argmax().item())
            label = label_names[idx]
            score = float(row[idx].item())
            compound = score if label == "positive" else (-score if label == "negative" else 0.0)
            out.append(SentimentResult(label=label, score=score, compound=compound))
        return out

    def _vader_analyze(self, text: str) -> SentimentResult:
        scores = self._vader.polarity_scores(text)
        compound = float(scores["compound"])
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return SentimentResult(label=label, score=abs(compound), compound=compound)

