"""One bounded read-only conversion preview, accepted through ordinary document transactions."""

from dataclasses import asdict, dataclass, field, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.curve_conversion import ConversionSpec
from anthroforge.core.curve_engines import decode
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port, ReadRevision
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import construction_policy, curve_sources, dependencies, object_operations, path_assets
from .conversion_geometry import ConversionInput, convert

if TYPE_CHECKING:
    from .session import Session


@dataclass
class ConversionPreview:
    token: str = ""
    target: str = ""
    document: str = ""
    job: str = ""
    asset: path_assets.PathAsset | None = None
    reads: tuple[ReadRevision, ...] = ()
    error: str = ""
    state: str = "idle"
    ports: set[Port] = field(default_factory=set)


def preview(
    session: "Session",
    curve: str,
    engine: str,
    mode: str = "EVALUATED",
    samples: int = 64,
    points: list[str] | None = None,
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    spec = ConversionSpec(curve, decode(engine, settings), mode, samples, tuple(points or ()))
    return start_preview(session, spec)


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
        kind="curve_path",
        publish_during_edit=True,
    )
    return configure_job(session, value, spec, job)


def configure_job(
    session: "Session", value: ConversionPreview, spec: ConversionSpec, job: Job
) -> Job:
    job.cancel = NativeCancellation(session.engine)
    job.reads = frozenset({spec.curve})
    job.observes = frozenset(dependencies.ports(session.document, Port(spec.curve, "path")))
    job.cleanup = partial(completed, value, job)
    job.workload = lambda _: Workload(candidates=spec.samples, triangles=spec.samples * 24)
    return job


def capture(
    session: "Session", value: ConversionPreview, spec: ConversionSpec, document: Any
) -> ConversionInput:
    value.ports = dependencies.ports(document, Port(spec.curve, "path"))
    value.reads = construction_policy.revisions(document, value.ports)
    source = curve_sources.source(document, spec.curve)
    value.state = "running"
    return ConversionInput(source, spec, session.resources.paths.get(source.result.asset))


def compute(session: "Session", value: ConversionInput, cancel: Any) -> path_assets.PathAsset:
    candidate = convert(session.engine, value, cancel.handle)
    return path_assets.evaluate(session.engine, candidate, cancel.handle)


def current(session: "Session", value: ConversionPreview) -> bool:
    if (
        str(session.document.id) != value.document
        or value.target not in session.document.registry.records
    ):
        return False
    return value.reads == construction_policy.revisions(session.document, value.ports)


def publish(session: "Session", value: ConversionPreview, asset: path_assets.PathAsset) -> None:
    if session.conversion is not value or not current(session, value):
        raise ValueError("The source changed; request a new conversion preview.")
    value.asset, value.state = asset, "ready"


def completed(value: ConversionPreview, job: Job, state: str) -> None:
    if state != "succeeded":
        value.asset, value.state, value.error = None, state, job.error


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
    value = session.conversion
    if value.job:
        session.scheduler.cancel_job(value.job, obsolete=True)
    session.conversion = ConversionPreview()
