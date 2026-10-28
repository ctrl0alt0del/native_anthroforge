"""Engine-wide cost/size/recency retention, independent of document ownership."""

from threading import RLock
from typing import Any

from .resource_footprint import Allocations


class CacheBudget:
    def __init__(self, budget: int = 4 * 1024**3) -> None:
        self.budget, self.age = budget, 0.0
        self.lock = RLock()
        self.allocations = Allocations()
        self.caches: list[Any] = []

    def attach(self, cache: Any) -> None:
        cache.pool, cache.lock = self, self.lock
        self.caches.append(cache)

    def trim(self) -> None:
        while self.allocations.bytes > self.budget:
            entries = ((cache, key) for cache in self.caches for key in cache.receipts)
            cache, key = min(entries, key=lambda entry: entry[0].receipts[entry[1]][2])
            self.age = max(self.age, cache.receipts[key][2])
            cache.remove(key, "aggregate_budget")

    def report(self) -> dict[str, int]:
        with self.lock:
            return dict(
                budget=self.budget,
                bytes=self.allocations.bytes,
                allocations=len(self.allocations.entries),
            )
