"""Read-only replacement jobs share bounded ownership, stale checks and explicit approvals."""

from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from . import dependencies, previews
from .construction_policy import revisions
from .replacement_reviews import Candidate, change_rows, current, require_unchanged


def start(session: Any, slot: str, target: str, worker: Any, kind: str, workload: Any) -> Any:
    previews.cancel(session, slot)
    value = previews.Preview[Candidate](
        str(uuid4()), target, str(session.document.id), state="queued"
    )
    setattr(session, slot, value)
    job = make_job(session, slot, value, worker, kind)
    job.workload = workload
    value.job = job.id
    session.scheduler.submit(job)
    return status(session, slot)


def make_job(session: Any, slot: str, value: Any, worker: Any, kind: str) -> Job:
    job = Job(
        "Assess replacement",
        frozenset(),
        partial(capture, session, value),
        worker,
        partial(publish, session, slot, value),
        key=slot,
        kind=kind,
        writes=False,
        publish_during_edit=True,
    )
    return configure_job(session, value, job)


def configure_job(session: Any, value: Any, job: Job) -> Job:
    job.cancel = NativeCancellation(session.engine)
    job.observes = frozenset(dependencies.graph(session.document))
    job.reads = frozenset(p.owner for p in job.observes)
    job.cleanup = partial(previews.completed, value, job)
    return job


def capture(session: Any, value: Any, document: Any) -> Any:
    value.ports = set(dependencies.graph(document))
    value.reads, value.state = revisions(document, value.ports), "running"
    return document, session.resources.snapshot()


def publish(session: Any, slot: str, value: Any, candidate: Candidate) -> None:
    if getattr(session, slot) is not value or not previews.current(session, value):
        raise ValueError("Replacement inputs changed; assess again.")
    require_unchanged(session, value.target, candidate)
    value.asset, value.state = candidate, "ready"


def status(session: Any, slot: str) -> dict[str, Any]:
    value = getattr(session, slot)
    state = "stale" if value.state == "ready" and not current(session, value) else value.state
    candidate = value.asset
    return dict(
        token=value.token,
        target=value.target,
        job_id=value.job,
        state=state,
        error=value.error,
        matching_correspondence=candidate.matching if candidate else None,
        changes=change_rows(session, candidate) if candidate else [],
    )


def ready(session: Any, slot: str, token: str) -> Any:
    from .replacement_status import validate_target

    value = getattr(session, slot)
    if (
        token != value.token
        or value.state != "ready"
        or not value.asset
        or not previews.current(session, value)
    ):
        raise ValueError("A current successful replacement assessment is required.")
    require_unchanged(session, value.target, value.asset)
    validate_target(session, slot, value.target)
    return value, value.asset


def require(session: Any, slot: str, token: str, approved: list[str]) -> Any:
    value, candidate = ready(session, slot, token)
    required = {row.key for row in candidate.changes}
    if len(set(approved)) != len(approved) or set(approved) != required:
        raise ValueError("Explicitly approve every listed rebind or discarded setting.")
    return value, candidate
