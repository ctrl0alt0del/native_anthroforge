"""Bounded recent samples for responsiveness diagnostics, never persisted as anatomy."""

from collections import defaultdict, deque


class Metrics:
    def __init__(self) -> None:
        self.samples: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=256))

    def observe(self, name: str, seconds: float) -> None:
        self.samples[name].append(seconds * 1000.0)

    def report(self) -> dict[str, dict[str, float]]:
        return {name: self.summarize(values) for name, values in self.samples.items() if values}

    @staticmethod
    def summarize(values: deque[float]) -> dict[str, float]:
        ordered = sorted(values)
        return {
            "count": len(values),
            "p95_ms": ordered[int((len(values) - 1) * 0.95)],
            "max_ms": max(values),
            "mean_ms": sum(values) / len(values),
        }
