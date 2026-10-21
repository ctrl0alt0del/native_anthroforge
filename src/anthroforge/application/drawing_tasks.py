"""Background fitting publishes a complete first-class curve and accepted native path."""

from dataclasses import dataclass, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import decode
from anthroforge.core.document import Document
from anthroforge.core.drawing import FitSettings
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.scheduling import Workload
from anthroforge.native import curve_editing, drawing
from anthroforge.native.mesh import NativeCancellation, doubles

from . import authored_jobs, dependencies, path_assets, placement_inputs, surface_providers
from .construction_policy import revisions

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class Request:
    metadata: dict[str, Any]
    samples: Any
    options: FitSettings
    projection: Any = None


def inputs(document: Document, request: Request) -> set[Port]:
    targets = request.projection["targets"] if request.projection else ()
    return dependencies.closure(
        dependencies.graph(document), surface_providers.ports(document, targets)
    )


def stroke_samples(points: list[list[float]]) -> Any:
    samples = doubles(points).copy()
    if samples.ndim != 2 or samples.shape[1] not in (3, 4) or not 2 <= len(samples) <= 100000:
        raise ValueError("A stroke requires between 2 and 100000 xyz or xyz/radius samples.")
    samples.flags.writeable = False
    return samples


def enqueue(session: "Session", request: Request, origin: int) -> str:
    if request.metadata["id"] in session.document.registry.records:
        return ""
    job = create_job(session, request, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, request, origin)
    job.workload = lambda _: Workload(
        affected=1, candidates=len(request.samples), bytes=request.samples.nbytes
    )
    job.provides = frozenset((Port(request.metadata["id"], "path"),))
    job.observes = job.prerequisites = frozenset(inputs(session.document, request))
    job.restart_on_input_change = True
    return session.scheduler.submit(job)


def create_job(session: "Session", request: Request, origin: int) -> Job:
    return Job(
        "Fit " + request.metadata["name"],
        frozenset((request.metadata["id"],)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session.engine, request),
        partial(publish, session, request, origin),
        kind="curve_draw",
        key="draw:" + request.metadata["id"],
    )


def compute(engine: Any, request: Request, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    samples = placement_inputs.confirmed(
        engine, document, resources, request.samples, request.projection, cancel.handle
    )
    item = fitted(engine, request, samples, cancel.handle)
    return document, item, path_assets.evaluate(engine, item, cancel.handle)


def fitted(engine: Any, request: Request, samples: Any, cancel: int) -> Curve:
    records = drawing.fit(engine, samples, request.options, cancel)
    points = tuple(curve_editing.unpack(CurvePoint(), row) for row in records)
    name = "POLYLINE" if request.options.method == "POLYLINE" else "BEZIER"
    return Curve(
        points, closed=request.options.closed, engine_settings=decode(name), **request.metadata
    )


def publish(session: "Session", request: Request, origin: int, payload: Any) -> None:
    from .object_creation import validate_parent

    document, item, asset = payload
    validate_parent(session, item)
    key = str(uuid4())
    result = EvaluationResult(key, 1, item.construction_revision)
    changed = replace(item, result=result)
    capture = authored_jobs.Capture(
        revisions(document, inputs(document, request)), partial(enqueue, session, request, origin)
    )
    authored_jobs.publish(
        session, origin, partial(authored_jobs.append_object, item=changed), capture
    )
    session.resources.paths[key] = asset
