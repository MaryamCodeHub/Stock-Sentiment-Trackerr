from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog

from src.core.config import settings


def configure_logging() -> None:
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    shared_processors: list[object] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        _add_service_info,
    ]

    if settings.log_format == "json":
        processors = shared_processors + [structlog.processors.JSONRenderer()]
    else:
        processors = shared_processors + [structlog.dev.ConsoleRenderer(colors=True)]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(
            file=open(settings.log_file, "a") if settings.is_production else sys.stdout
        ),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )


def _add_service_info(logger, method, event_dict):
    event_dict["service"] = "stock-sentiment-tracker"
    event_dict["version"] = settings.app_version
    event_dict["environment"] = settings.environment
    return event_dict

