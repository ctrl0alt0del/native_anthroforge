"""Causal request urgency and temporary inheritance through active prerequisites."""

from collections.abc import Callable
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.core.scheduling import QueueDemand, RequestUrgency

from .job_registry import JobRegistry


def merge(job: Job, urgency: RequestUrgency | None) -> None:
    if urgency is None:
        return
    current = job.urgency
    job.urgency = RequestUrgency(
        urgency.interactive or bool(current and current.interactive),
        min(urgency.since, current.since) if current else urgency.since,
    )


def demand(job: Job) -> QueueDemand:
    assert job.urgency is not None
    queued = job.created if job.queued_since is None else job.queued_since
    return QueueDemand(
        job.priority + 100 * job.urgency.interactive, job.urgency.since, queued, job.id
    )


def live(job: Job) -> bool:
    return job.active and not job.obsolete and not (job.cancel and job.cancel.is_set())


def providers(registry: JobRegistry, job: Job, active: dict[str, Job]) -> set[str]:
    index = registry.indexes["provides"]
    ids = set().union(*(index.get(port, ()) for port in job.prerequisites))
    return (ids & active.keys()) - {job.id}


def donate(root: Job, edges: dict[str, set[str]], ranks: dict[str, QueueDemand]) -> None:
    pending, rank = [root.id], demand(root)
    while pending:
        key = pending.pop()
        if key not in ranks:
            ranks[key] = rank
            pending.extend(edges[key])


class TaskPriorities:
    def __init__(self) -> None:
        self.source: Job | None = None

    def capture(self, job: Job, now: float) -> None:
        since = now if job.queued_since is None else job.queued_since
        merge(job, RequestUrgency(job.interactive, since))
        if self.source is not None:
            merge(job, self.source.urgency)

    def call(self, job: Job, function: Callable[..., Any], *args: Any) -> Any:
        previous, self.source = self.source, job
        try:
            return function(*args)
        finally:
            self.source = previous

    def ordered(self, registry: JobRegistry) -> list[Job]:
        active = {key: job for key, job in registry.active.items() if live(job)}
        edges = {key: providers(registry, job, active) for key, job in active.items()}
        ranks: dict[str, QueueDemand] = {}
        for job in sorted(active.values(), key=lambda item: demand(item).key):
            donate(job, edges, ranks)
        for key, job in active.items():
            job.queue_demand = ranks[key]
        return sorted(
            (job for job in active.values() if job.state == "queued"),
            key=lambda job: (*ranks[job.id].key, job.created),
        )
