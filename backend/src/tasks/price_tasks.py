from __future__ import annotations

from src.tasks.celery_app import celery_app


@celery_app.task(name="tasks.fetch_prices")
def fetch_prices() -> None:
    # Scaffold task — implement periodic collection next.
    return None

