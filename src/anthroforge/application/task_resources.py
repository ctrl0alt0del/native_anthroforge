"""Shared concurrency admission; estimates never terminate or reject isolated work."""

import os
from collections.abc import Callable, Iterable

from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import ResourceDemand

from .worker_memory import available


def demand(job: Job) -> ResourceDemand:
    return job.assessment.schedule.resources if job.assessment else ResourceDemand()


def threads(row: ResourceDemand, capacity: int) -> int:
    return min(capacity, row.threads or capacity)


class Admission:
    def __init__(
        self, cpus: Callable[[], int | None] = os.cpu_count, memory: Callable[[], int] = available
    ) -> None:
        self.cpus, self.memory = cpus, memory

    def waiting(self, job: Job, active: Iterable[Job]) -> str:
        running = [other for other in active if other is not job and other.future is not None]
        if not running:
            return ""
        capacity = max(1, self.cpus() or 1)
        claims = [demand(other) for other in running]
        needed = demand(job)
        used = sum(threads(row, capacity) for row in claims)
        if used + threads(needed, capacity) > capacity:
            return "Waiting for compute capacity"
        free = self.memory()
        if sum(row.memory_bytes for row in claims) + needed.memory_bytes > max(0, free):
            return "Waiting for estimated working memory"
        return ""
