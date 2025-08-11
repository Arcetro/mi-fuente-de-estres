from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

from policy.core import SessionState


class SessionStoreRedis:
    def __init__(self, url: str, ttl_seconds: int):
        if not redis:
            raise RuntimeError("redis package not available")
        self.client = redis.from_url(url)
        self.ttl_seconds = ttl_seconds

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def get(self, session_id: str) -> SessionState:
        data = self.client.get(self._key(session_id))
        if not data:
            state = SessionState()
            self.set(session_id, state)
            return state
        obj = json.loads(data)
        state = SessionState(
            pending_slot=obj.get("pending_slot"),
            attempts=obj.get("attempts", {}),
            collected=obj.get("collected", {}),
        )
        return state

    def set(self, session_id: str, state: SessionState) -> None:
        payload = json.dumps(
            {
                "pending_slot": state.pending_slot,
                "attempts": state.attempts,
                "collected": state.collected,
            }
        )
        self.client.setex(self._key(session_id), self.ttl_seconds, payload)

    def reset(self, session_id: str) -> None:
        self.client.delete(self._key(session_id))


