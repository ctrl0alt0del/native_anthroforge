"""Inflation candidates are read-only job outputs; acceptance is one ordinary edit."""

from dataclasses import asdict, dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core import tissue_policy
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.mesh import Mesh, NativeCancellation

from . import dependencies, previews, tissue_evaluation, tissue_operations, tissue_part_operations
from .construction_policy import revisions


@dataclass(frozen=True)
class Candidate:
    item: TissueVCP
    mesh: Mesh
    part: str
    side: str
    changes: dict[str, Any]


def preview(
    session: Any, target: str, changes: Any, part: str = "main", side: str = "a", reset: str = ""
) -> Any:
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit before previewing inflation.")
    options: dict[str, Any] = dict(
        target=target, changes=dict(changes), part=part, side=side, reset=reset
    )
    definition(session, **options)
    return start(session, target, options)


def start(session: Any, target: str, options: Any) -> Any:
    previews.cancel(session, "tissue_preview")
    value = previews.Preview[Candidate](
        str(uuid4()), target, str(session.document.id), state="queued"
    )
    session.tissue_preview = value
    job = make_job(session, value, options)
    value.job = job.id
    session.scheduler.submit(job)
    return status(session)


def definition(session: Any, target: str, changes: Any, part: str, side: str, reset: str) -> Any:
    item = tissue_operations.tissue(session, target)
    changes = reset_changes(session, item, changes, part, side, reset)
    edited = tissue_operations.edited_parts(session, item, part, side, changes)
    tissue_policy.validate(edited, session.document.registry.records)
    tissue_operations.require_inflation_topology(session, item, edited)
    settings = getattr(tissue_part_operations.selected(edited, part), side).inflation
    return edited, asdict(settings)


def reset_changes(session: Any, item: Any, changes: Any, part: str, side: str, reset: str) -> Any:
    if not reset:
        return changes
    current = getattr(tissue_part_operations.selected(item, part), side).inflation
    if reset == "PROFILE":
        depth = changes.get("amount", current.amount)
        return dict(changes, profile=tissue_part_operations.profile_value(session, depth))
    if reset == "CONTROL":
        return dict(changes, control=tissue_part_operations.control_value(session, item, part))
    raise ValueError("Choose PROFILE or CONTROL initialization.")


def make_job(session: Any, value: Any, options: Any) -> Job:
    job = Job(
        "Preview tissue inflation",
        frozenset(),
        partial(capture, session, value, options),
        partial(compute, session, options),
        partial(publish, session, value),
        key="tissue_preview",
        kind="tissue_rest",
        writes=False,
        publish_during_edit=True,
    )
    configure_job(session, value, job)
    return job


def configure_job(session: Any, value: Any, job: Job) -> None:
    job.cancel = NativeCancellation(session.engine)
    job.observes = frozenset(inputs(session.document, value.target))
    job.prerequisites = job.observes - {Port(value.target, "rest")}
    job.reads = frozenset(p.owner for p in job.observes)
    job.cleanup = partial(previews.completed, value, job)
    from .tissue_tasks import workload

    job.workload = partial(workload, session, value.target, "rest")


def inputs(document: Any, target: str) -> set[Port]:
    return dependencies.ports(document, Port(target, "rest"))


def capture(session: Any, value: Any, options: Any, document: Any) -> Any:
    item, settings = definition(session, **options)
    value.ports, value.state = inputs(document, value.target), "running"
    value.reads = revisions(document, value.ports)
    return document, session.resources.snapshot(), item, settings


def compute(session: Any, options: Any, payload: Any, cancel: Any) -> Candidate:
    document, resources, item, settings = payload
    output = tissue_evaluation.rest(session.engine, document, resources, item, cancel.handle)
    assert output.mesh is not None
    return Candidate(item, output.mesh, options["part"], options["side"], settings)


def publish(session: Any, value: Any, candidate: Candidate) -> None:
    if session.tissue_preview is not value or not previews.current(session, value):
        raise ValueError("Tissue inputs changed; request a new inflation preview.")
    value.asset, value.state = candidate, "ready"


def status(session: Any) -> dict[str, Any]:
    value = session.tissue_preview
    state = (
        "stale" if value.state == "ready" and not previews.current(session, value) else value.state
    )
    return dict(
        token=value.token,
        target=value.target,
        job_id=value.job,
        state=state,
        error=value.error,
        settings=value.asset.changes if value.asset else {},
        part=value.asset.part if value.asset else "",
        side=value.asset.side if value.asset else "",
    )


def accept(session: Any, token: str) -> None:
    value = session.tissue_preview
    if (
        token != value.token
        or value.state != "ready"
        or not value.asset
        or not previews.current(session, value)
    ):
        raise ValueError("A current successful inflation preview is required.")
    candidate = value.asset
    current = tissue_operations.tissue(session, value.target)
    tissue_operations.install_inflation(
        session, current, replace(current, parts=candidate.item.parts)
    )
    cancel(session)


def cancel(session: Any) -> None:
    previews.cancel(session, "tissue_preview")
