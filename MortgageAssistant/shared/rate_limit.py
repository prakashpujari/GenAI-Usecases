from __future__ import annotations

import time
from collections import defaultdict


class InMemoryRateLimiter:
    def __init__(self, rps: int) -> None:
        self.rps = rps
        self.calls = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        window = now - 1
        calls = [t for t in self.calls[key] if t >= window]
        self.calls[key] = calls
        if len(calls) >= self.rps:
            return False
        self.calls[key].append(now)
        return True
