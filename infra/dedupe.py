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


def build_deduper() -> object:
    ttl_minutes = int(os.environ.get("DEDUPE_TTL_MINUTES", "10"))
    ttl_seconds = ttl_minutes * 60
    url = os.environ.get("REDIS_URL")
    if url and redis:
        return DeduperRedis(url, ttl_seconds)
    return DeduperMemory(ttl_seconds)


