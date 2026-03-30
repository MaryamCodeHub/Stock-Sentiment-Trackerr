from __future__ import annotations

import functools
import hashlib
import json
import logging
from typing import Any, Callable

from src.core.redis_client import redis_client

logger = logging.getLogger(__name__)


def cache_response(ttl: int = 300) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache_key = _build_key(func.__name__, args, kwargs)
            cached = await redis_client.get(cache_key)
            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis_client.setex(cache_key, ttl, _serialize(result))
            return result

        return wrapper

    return decorator


def _build_key(func_name: str, args: tuple, kwargs: dict) -> str:
    key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
    return f"sst:cache:{hashlib.md5(key_data.encode()).hexdigest()}"


def _serialize(obj: Any) -> str:
    if hasattr(obj, "model_dump"):
        return obj.model_dump_json()
    if isinstance(obj, list):
        items = [
            item.model_dump() if hasattr(item, "model_dump") else item for item in obj
        ]
        return json.dumps(items, default=str)
    return json.dumps(obj, default=str)

