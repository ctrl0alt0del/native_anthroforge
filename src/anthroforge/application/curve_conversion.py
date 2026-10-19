"""One bounded read-only conversion preview, accepted through ordinary document transactions."""

from dataclasses import asdict, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.curve_conversion import ConversionSpec
from anthroforge.core.curve_engines import decode
from anthroforge.core.fibers import Fiber, FiberEdit
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.core.routing_obstacles import graph as routing_graph
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import (
    construction_policy,
    curve_edit_state,
    curve_evaluation,
    curve_sources,
    dependencies,
    object_operations,
    path_assets,
)
from .attachment_candidates import eligible
from .conversion_geometry import ConversionInput, convert
from .previews import Preview
from .previews import completed as completed
from .previews import current as current

if TYPE_CHECKING:
    from .session import Session

ConversionPreview = Preview[path_assets.PathAsset]


def preview(
    session: "Session",
    curve: str,
    engine: str,
    mode: str = "EVALUATED",
    samples: int = 64,
    points: list[str] | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = conversion_spec(session, curve, engine, mode, samples, points, settings)
    return start_preview(session, spec)


def conversion_spec(
    session: Any,
    curve: str,
    engine: str,
    mode: str,
    samples: int,
    points: list[str] | None,
    settings: Any,
) -> ConversionSpec:
    chosen = conversion_points(session, curve, points)
    if engine == "ROUTED":
        mode = "AUTHORED"
        settings = dict(settings or {})
        settings.setdefault("samples", max(samples, len(chosen)))
    return ConversionSpec(curve, decode(engine, settings), mode, samples, chosen)


def conversion_points(session: Any, curve: str, points: list[str] | None) -> tuple[str, ...]:
    source = curve_sources.source(session.document, curve)
    return tuple(p.id for p in source.points) if points is None else tuple(points)


def start_preview(session: "Session", spec: ConversionSpec) -> dict[str, Any]:
    require_editable(session, spec.curve)
    cancel(session)
    value = ConversionPreview(str(uuid4()), spec.curve, str(session.document.id), state="queued")
    session.conversion = value
    job = make_job(session, value, spec)
    value.job = job.id
    session.scheduler.submit(job)
    return status(session)


def require_editable(session: "Session", curve: str) -> None:
    object_operations.editable(session, curve)
    curve_sources.source(session.document, curve)
    if session.history.before is not None:
        raise ValueError("Finish the current edit before changing the curve engine.")
    for consumer in curve_sources.consumers(session.document, {curve}):
        construction_policy.require_topology_edit(session.document, consumer)


def make_job(session: "Session", value: ConversionPreview, spec: ConversionSpec) -> Job:
    job = Job(
        "Preview curve conversion",
        frozenset(),
        partial(capture, session, value, spec),
        partial(compute, session),
        partial(publish, session, value),
        key="curve_conversion",
        writes=False,
        kind="curve_routing" if spec.settings.kind == "ROUTED" else "curve_path",
        publish_during_edit=True,
    )
    return configure_job(session, value, spec, job)


def configure_job(
    session: "Session", value: ConversionPreview, spec: ConversionSpec, job: Job
) -> Job:
    job.cancel = NativeCancellation(session.engine)
    job.observes = frozenset(preview_ports(session.document, spec))
    job.reads = frozenset(port.owner for port in job.observes)
    job.cleanup = partial(completed, value, job)
    job.workload = lambda _: Workload(candidates=spec.samples, triangles=spec.samples * 24)
    return job


def capture(
    session: "Session", value: ConversionPreview, spec: ConversionSpec, document: Any
) -> Any:
    value.ports = preview_ports(document, spec)
    value.reads = construction_policy.revisions(document, value.ports)
    source = curve_edit_state.current(session, curve_sources.source(document, spec.curve))
    value.state = "running"
    inputs = ConversionInput(source, spec, session.resources.paths.get(source.result.asset))
    return inputs, document, session.resources.snapshot()


def compute(session: "Session", payload: Any, cancel: Any) -> path_assets.PathAsset:
    value, document, resources = payload
    candidate = convert(session.engine, value, cancel.handle)
    if isinstance(candidate, Fiber):
        edit = FiberEdit(value.source.result.asset, eligible(document, candidate.id))
        candidate = replace(candidate, edit=edit)
    return curve_evaluation.evaluate_item(
        session.engine, document, resources, candidate, cancel.handle
    ).asset


def preview_ports(document: Any, spec: ConversionSpec) -> set[Port]:
    original = curve_sources.source(document, spec.curve)
    candidate = replace(original, engine_settings=spec.settings)
    graph = routing_graph(document, candidate)
    inputs = {Port(original.id, "path")}
    if isinstance(candidate, Fiber):
        from .surface_providers import ports

        inputs |= ports(document, eligible(document, candidate.id))
    return dependencies.closure(graph, inputs)


def publish(session: "Session", value: ConversionPreview, asset: path_assets.PathAsset) -> None:
    if session.conversion is not value or not current(session, value):
        raise ValueError("The source changed; request a new conversion preview.")
    value.asset, value.state = asset, "ready"


def status(session: "Session") -> dict[str, Any]:
    value = session.conversion
    state = "stale" if value.state == "ready" and not current(session, value) else value.state
    candidate = value.asset.authored if value.asset is not None else None
    return dict(
        token=value.token,
        target=value.target,
        job_id=value.job,
        state=state,
        error=value.error,
        engine=candidate.engine if candidate else "",
        points=len(candidate.points) if candidate else 0,
        settings=asdict(candidate.engine_settings) if candidate else {},
    )


def accept(session: "Session", token: str) -> None:
    candidate = require_candidate(session, token).authored
    source = curve_sources.source(session.document, candidate.id)
    for consumer in curve_sources.consumers(session.document, {candidate.id}):
        construction_policy.require_topology_edit(session.document, consumer)
    changed = replace(source, points=candidate.points, engine_settings=candidate.engine_settings)
    object_operations.install(session, changed)
    cancel(session)


def require_candidate(session: "Session", token: str) -> path_assets.PathAsset:
    value = session.conversion
    if (
        token != value.token
        or value.state != "ready"
        or value.asset is None
        or not current(session, value)
    ):
        raise ValueError("A current successful conversion preview is required.")
    return value.asset


def cancel(session: "Session") -> None:
    from . import previews

    previews.cancel(session, "conversion")
