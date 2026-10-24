"""Active producer/consumer links maintained at the registry mutation boundary."""

from typing import Any

from anthroforge.core.jobs import Job


class JobDependencies:
    def __init__(self) -> None:
        self.providers: dict[str, set[str]] = {}
        self.consumers: dict[str, set[str]] = {}

    def add(self, registry: Any, job: Job) -> None:
        self.providers.setdefault(job.id, set())
        self.consumers.setdefault(job.id, set())
        for port in job.prerequisites:
            for provider in registry.indexes["provides"].get(port, ()):
                self.connect(provider, job.id)
        for port in job.provides:
            for consumer in registry.indexes["port"].get(port, ()):
                if port in registry.active[consumer].prerequisites:
                    self.connect(job.id, consumer)

    def connect(self, provider: str, consumer: str) -> None:
        if provider != consumer:
            self.providers.setdefault(consumer, set()).add(provider)
            self.consumers.setdefault(provider, set()).add(consumer)

    def remove(self, key: str) -> None:
        for provider in self.providers.pop(key, ()):
            self.consumers[provider].discard(key)
        for consumer in self.consumers.pop(key, ()):
            self.providers[consumer].discard(key)

    def live(self, active: dict[str, Job]) -> dict[str, set[str]]:
        return {key: self.providers.get(key, set()) & active.keys() for key in active}
