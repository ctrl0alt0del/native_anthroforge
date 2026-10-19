"""Surface alignment candidates remain outside document/history until explicit acceptance."""

from dataclasses import asdict, dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.jobs import Job
from anthroforge.core.object_registry import validate_sources
from anthroforge.core.results import Port
from anthroforge.core.surfaces import Surface
from anthroforge.native.mesh import Mesh, NativeCancellation

from . import construction_tasks, object_creation, previews, surface_jobs
from . import surface_operations as operations
from .assets import Asset
from .construction_policy import require_topology_edit, revisions
from .evaluation_results import accepted_result
from .object_revisions import authored


@dataclass(frozen=True)
class Candidate:
    surface: Surface
    mesh: Mesh


def preview(session: Any, target: str = "", curves: list[str] | None = None, **options: Any) -> Any:
    if session.history.before is not None or session.waiting_save:
        raise ValueError("Finish the current edit before previewing surface alignment.")
    item = operations.editable(session, target) if target else new_surface(session, curves, options)
    require_topology_edit(session.document, item.id)
    validate_sources(item, session.document.registry.records)
    previews.cancel(session, "surface_preview")
    value = previews.Preview[Candidate](
        str(uuid4()), target, str(session.document.id), state="queued"
    )
    session.surface_preview = value
    job = make_job(session, value, item)
    value.job = job.id
    session.scheduler.submit(job)
    return status(session)


def new_surface(session: Any, curves: list[str] | None, options: dict[str, Any]) -> Surface:
    common = {
        key: options.pop(key, default)
        for key, default in dict(kind="LOFT", name="Surface", parent="", owner="").items()
    }
    return operations.configured(operations.new_surface(session, curves or [], **common), options)


def make_job(session: Any, value: previews.Preview[Candidate], item: Surface) -> Job:
    job = Job(
        "Preview surface alignment",
        frozenset(),
        partial(capture, session, value, item),
        partial(compute, session, item, bool(value.target)),
        partial(publish, session, value),
        key="surface_preview",
        kind="surface_layout",
        writes=False,
        publish_during_edit=True,
    )
    return configure_job(session, value, item, job)


def configure_job(session: Any, value: previews.Preview[Candidate], item: Surface, job: Job) -> Job:
    job.cancel = NativeCancellation(session.engine)
    job.observes = frozenset(inputs(session.document, item, bool(value.target)))
    job.prerequisites = job.observes - {Port(item.id, "geometry")}
    job.reads = frozenset(port.owner for port in job.observes)
    job.cleanup = partial(previews.completed, value, job)
    job.workload = lambda document: construction_tasks.surface_workload(session, item, document)
    return job


def inputs(document: Any, item: Surface, existing: bool) -> set[Port]:
    from . import dependencies

    ports = surface_jobs.inputs(document, item, existing)
    if item.parent:
        ports.add(Port(item.parent, "pose"))
    return dependencies.closure(dependencies.graph(document), ports)


def capture(session: Any, value: previews.Preview[Candidate], item: Surface, document: Any) -> Any:
    value.ports = inputs(document, item, bool(value.target))
    value.reads = revisions(document, value.ports)
    value.state = "running"
    return document, session.resources.snapshot()


def compute(session: Any, item: Surface, existing: bool, payload: Any, cancel: Any) -> Candidate:
    _, placed, mesh = surface_jobs.compute(session, item, existing, payload, cancel)
    return Candidate(placed, mesh)


def publish(session: Any, value: previews.Preview[Candidate], candidate: Candidate) -> None:
    if session.surface_preview is not value or not previews.current(session, value):
        raise ValueError("Surface inputs changed; request a new alignment preview.")
    value.asset, value.state = candidate, "ready"


def status(session: Any) -> dict[str, Any]:
    value = session.surface_preview
    state = (
        "stale" if value.state == "ready" and not previews.current(session, value) else value.state
    )
    item = value.asset.surface if value.asset else None
    return dict(
        token=value.token,
        target=value.target,
        job_id=value.job,
        state=state,
        error=value.error,
        object_id=item.id if item else "",
        alignment=[asdict(a) for a in item.alignment] if item else [],
    )


def require_candidate(session: Any, token: str) -> Candidate:
    value = session.surface_preview
    if (
        token != value.token
        or value.state != "ready"
        or not value.asset
        or not previews.current(session, value)
    ):
        raise ValueError("A current successful surface preview is required.")
    candidate = value.asset
    assert isinstance(candidate, Candidate)
    return candidate


def accept(session: Any, token: str) -> str:
    candidate = require_candidate(session, token)
    value, item = session.surface_preview, candidate.surface
    require_topology_edit(session.document, item.id)
    item = accepted_definition(session, item, value.target)
    ports = {p for p in value.ports if p.owner != item.id}
    key = str(uuid4())
    item = replace(item, result=accepted_result(session.document, item, ports, key))
    install(session, item, candidate.mesh, key, bool(value.target))
    previews.cancel(session, "surface_preview")
    return item.id


def accepted_definition(session: Any, item: Surface, target: str) -> Surface:
    if target:
        before = operations.editable(session, target)
        return authored(before, replace(before, alignment=item.alignment, across=item.across))
    object_creation.placement(session, item.parent, next(iter(item.owners), ""), None)
    validate_sources(item, session.document.registry.records)
    return item


def install(session: Any, item: Surface, mesh: Mesh, key: str, existing: bool) -> None:
    objects = tuple(item if o.id == item.id else o for o in session.document.objects)
    if not existing:
        objects = (*objects, item)
    session.scheduler.invalidate_ports({Port(item.id, "geometry")})
    session.replace_document(objects=objects)
    session.assets[key] = Asset(mesh, "generated", "", 1.0, False)
    construction_tasks.propagate_result(session, item.id)


def cancel(session: Any) -> None:
    previews.cancel(session, "surface_preview")
