from __future__ import annotations

from src.tasks.celery_app import celery_app


@celery_app.task(name="tasks.compute_sentiment")
def compute_sentiment() -> None:
    # Scaffold task — implement periodic sentiment computation next.
    return None

