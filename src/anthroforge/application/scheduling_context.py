"""Coordinator-owned namespaces; one executor, resource admission and inline budget."""

from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import Any, cast

from anthroforge.core.document import Document

from .job_registry import JobRegistry
from .task_priorities import TaskPriorities


@dataclass
class SchedulingContext:
    checkpoint: Document
    registry: JobRegistry = field(default_factory=JobRegistry)
    epoch: int = 0
    coalescing: dict[str, Any] = field(default_factory=dict)
    priorities: TaskPriorities = field(default_factory=TaskPriorities)
    publishing: str = ""
    publication_contexts: tuple[str, ...] = ()
    annotate: Any = lambda job, document: None
    before_dispatch: Any = lambda job, document: None
    observer: Any = lambda job, phase: None


class SchedulingField[T]:
    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: Any = None) -> T:
        if instance is None:
            return cast(T, self)
        return cast(T, getattr(instance.scheduling_contexts[instance.context], self.name))

    def __set__(self, instance: Any, value: T) -> None:
        setattr(instance.scheduling_contexts[instance.context], self.name, value)


def initialize(coordinator: Any, document: Document) -> None:
    coordinator.context = ""
    coordinator.scheduling_contexts = {"": SchedulingContext(document)}
    coordinator.context_scope = lambda key: nullcontext()


def all_active(coordinator: Any) -> tuple[Any, ...]:
    return tuple(
        job
        for state in coordinator.scheduling_contexts.values()
        for job in state.registry.active.values()
    )


def pending(coordinator: Any, writes_only: bool) -> bool:
    return any(job.writes or not writes_only for job in all_active(coordinator))


def tick(coordinator: Any) -> None:
    coordinator.service_tick()
    for key in tuple(coordinator.scheduling_contexts):
        with coordinator.context_scope(key):
            coordinator.tick_context()
    coordinator.service_tick()
    coordinator.sample_resources()


def close(coordinator: Any) -> None:
    coordinator.service_tick = lambda: None
    for key in tuple(coordinator.scheduling_contexts):
        with coordinator.context_scope(key):
            for job in coordinator.active_jobs:
                coordinator.cancel_job(job.id, reason="session_closed")
    coordinator.pool.shutdown(wait=True, cancel_futures=True)
    coordinator.tick()
