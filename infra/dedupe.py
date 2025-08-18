from __future__ import annotations

import os
import time
from typing import Dict, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class DeduperMemory:
    def __init__(self, ttl_seconds: int = 600):
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, float] = {}

    def add_if_new(self, key: str) -> bool:
        now = time.time()
        # cleanup
        expired = [k for k, exp in self._store.items() if exp <= now]
        for k in expired:
            self._store.pop(k, None)
        if key in self._store:
            return False
        self._store[key] = now + self.ttl_seconds
        return True


class DeduperRedis:
    def __init__(self, url: str, ttl_seconds: int = 600):
        if not redis:
            raise RuntimeError("redis package not available")
        self.ttl_seconds = ttl_seconds
        self.client = redis.from_url(url)

    def add_if_new(self, key: str) -> bool:
        # SET key 1 NX EX ttl
        return bool(self.client.set(key, 1, nx=True, ex=self.ttl_seconds))


from config.settings import settings

def build_deduper() -> object:
    ttl_seconds = settings.DEDUPE_TTL_MINUTES * 60
    url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    if redis:
        try:
            # Check if redis is available
            redis.from_url(url).ping()
            return DeduperRedis(url, ttl_seconds)
        except redis.exceptions.ConnectionError:
            pass
    return DeduperMemory(ttl_seconds)


