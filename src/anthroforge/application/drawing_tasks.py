"""Background fitting publishes a complete first-class curve and accepted native path."""

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.document import Document
from anthroforge.core.drawing import FitSettings
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.scheduling import Workload
from anthroforge.native import curve_editing, drawing
from anthroforge.native.mesh import NativeCancellation, doubles

from . import authored_jobs, path_assets

if TYPE_CHECKING:
    from .session import Session


def stroke_samples(points: list[list[float]]) -> Any:
    samples = doubles(points).copy()
    if samples.ndim != 2 or samples.shape[1] not in (3, 4) or not 2 <= len(samples) <= 100000:
        raise ValueError("A stroke requires between 2 and 100000 xyz or xyz/radius samples.")
    samples.flags.writeable = False
    return samples


def enqueue(
    session: "Session", metadata: dict[str, Any], samples: Any, options: FitSettings, origin: int
) -> str:
    if metadata["id"] in session.document.registry.records:
        return ""
    job = create_job(session, metadata, samples, options, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, metadata, samples, options, origin)
    job.workload = lambda _: Workload(affected=1, candidates=len(samples), bytes=samples.nbytes)
    job.provides = frozenset((Port(metadata["id"], "path"),))
    return session.scheduler.submit(job)


def create_job(
    session: "Session", metadata: dict[str, Any], samples: Any, options: FitSettings, origin: int
) -> Job:
    return Job(
        "Fit " + metadata["name"],
        frozenset((metadata["id"],)),
        lambda document: document,
        partial(compute, session, metadata, samples, options),
        partial(publish, session, origin),
        kind="curve_draw",
        key="draw:" + metadata["id"],
    )


def compute(
    session: "Session",
    metadata: dict[str, Any],
    samples: Any,
    options: FitSettings,
    document: Document,
    cancel: Any,
) -> Any:
    records = drawing.fit(session.engine, samples, options, cancel.handle)
    points = tuple(curve_editing.unpack(CurvePoint(), row) for row in records)
    engine = "POLYLINE" if options.method == "POLYLINE" else "BEZIER"
    item = Curve(points, closed=options.closed, engine=engine, **metadata)
    return item, path_assets.evaluate(session.engine, item, cancel.handle)


def publish(session: "Session", origin: int, payload: Any) -> None:
    from .object_creation import validate_parent

    item, asset = payload
    validate_parent(session, item)
    key = str(uuid4())
    result = EvaluationResult(key, 1, item.construction_revision)
    changed = replace(item, result=result)
    authored_jobs.publish(session, origin, partial(authored_jobs.append_object, item=changed))
    session.resources.paths[key] = asset
