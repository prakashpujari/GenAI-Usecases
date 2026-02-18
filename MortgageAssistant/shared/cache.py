from __future__ import annotations

import time
from typing import Dict, List, Tuple


class EmbeddingCache:
    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: Dict[str, Tuple[float, List[float]]] = {}

    def get(self, key: str) -> List[float] | None:
        entry = self._store.get(key)
        if not entry:
            return None
        created_at, value = entry
        if time.time() - created_at > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: List[float]) -> None:
        self._store[key] = (time.time(), value)
