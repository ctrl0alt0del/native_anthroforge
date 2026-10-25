"""Read-only candidate ownership and revision validity, independent of candidate geometry."""

from dataclasses import dataclass, field
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.core.results import Port, ReadRevision

from .construction_policy import revisions


@dataclass
class Preview[T]:
    token: str = ""
    target: str = ""
    document: str = ""
    job: str = ""
    asset: T | None = None
    reads: tuple[ReadRevision, ...] = ()
    error: str = ""
    state: str = "idle"
    ports: set[Port] = field(default_factory=set)


def current(session: Any, value: Preview[Any]) -> bool:
    document = session.document
    available = document.registry.records.keys() | document.mirrors.instances.keys()
    if str(document.id) != value.document:
        return False
    if value.target and value.target not in available:
        return False
    if any(port.owner not in available for port in value.ports):
        return False
    return value.reads == revisions(document, value.ports)


def completed(value: Preview[Any], job: Job, state: str) -> None:
    if state != "succeeded":
        value.asset, value.state, value.error = None, state, job.error


def cancel(session: Any, slot: str) -> None:
    value = getattr(session, slot)
    if value.job:
        session.scheduler.cancel_job(value.job, obsolete=True)
    setattr(session, slot, Preview())
