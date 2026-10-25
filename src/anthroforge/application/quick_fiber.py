"""Atomic surface-click Fiber creation; provisional seeds never enter authored history."""

from dataclasses import dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings, RoutingSettings
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.routing_obstacles import references
from anthroforge.native.mesh import NativeCancellation

from . import (
    authored_jobs,
    curve_evaluation,
    dependencies,
    fiber_operations,
    fiber_tasks,
    object_creation,
    path_assets,
    path_policy,
    surface_providers,
)
from .construction_policy import revisions
from .operations import require_name


@dataclass(frozen=True)
class Request:
    seed: Curve
    binding: fiber_operations.FiberCreation


def create(session: Any, points: list[dict[str, Any]], owner: str = "", name: str = "Fiber") -> str:
    if not 2 <= len(points) <= 100000:
        raise ValueError("Place at least two surface points for a Fiber.")
    metadata = object_creation.placement(session, "", owner, None)
    authored = tuple(CurvePoint(position=tuple(row["position"])) for row in points)
    seed = Curve(authored, name=require_name(name), engine_settings=PolylineSettings(), **metadata)
    values = [dict(row, point=p.id) for row, p in zip(points, authored, strict=True)]
    if any(not row.get("target") for row in values):
        raise ValueError("Every placed Fiber point needs its clicked surface target.")
    bindings = fiber_operations.requested_bindings(session, seed, values)
    mapping = {key: key for key in (seed.id, *(p.id for p in seed.points))}
    request = Request(seed, fiber_operations.creation(seed, mapping, bindings, seed.name))
    return authored_jobs.begin(session, partial(enqueue, session, request))


def routed(request: Request) -> Curve:
    return replace(request.seed, engine_settings=RoutingSettings())


def inputs(document: Any, request: Request) -> set[Port]:
    targets = set(fiber_tasks.capture_targets(document, request.binding))
    targets.update(references(document, routed(request)))
    return dependencies.closure(
        dependencies.graph(document), surface_providers.ports(document, targets)
    )


def enqueue(session: Any, request: Request, origin: int) -> str:
    job = make_job(session, request, origin)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, request, origin)
    job.restart_on_input_change = True
    job.observes = job.prerequisites = frozenset(inputs(session.document, request))
    job.reads = frozenset(p.owner for p in job.observes)
    job.provides = frozenset((Port(request.seed.id, "path"),))
    job.workload = partial(workload, session, request)
    return str(session.scheduler.submit(job))


def make_job(session: Any, request: Request, origin: int) -> Job:
    return Job(
        "Place " + request.seed.name,
        frozenset((request.seed.id,)),
        lambda document: (document, session.resources.snapshot(), session.preferences.value),
        partial(compute, session, request),
        partial(publish, session, request, origin),
        key="fiber:" + request.seed.id,
        kind="fiber_create",
    )


def workload(session: Any, request: Request, document: Any) -> Any:
    value = path_policy.routing_workload(session, routed(request), document)
    return replace(value, candidates=value.candidates + 4 * len(request.seed.points))


def seeded(engine: Any, document: Any, resources: Any, seed: Curve, cancel: int) -> Any:
    key = str(uuid4())
    resources.paths[key] = path_assets.evaluate(engine, seed, cancel)
    seed = replace(seed, result=EvaluationResult(key, 1, seed.construction_revision))
    return replace(document, objects=(*document.objects, seed))


def compute(session: Any, request: Request, payload: Any, cancel: Any) -> Any:
    document, resources, preferences = payload
    provisional = seeded(session.engine, document, resources, request.seed, cancel.handle)
    _, fiber, _, attachment = fiber_tasks.compute(
        session, request.binding, (provisional, resources), cancel
    )
    fiber = replace(fiber, engine_settings=RoutingSettings())
    resources.attachments[fiber.attachment_asset] = attachment
    provisional = replace(document, objects=(*document.objects, fiber))
    result = route_created(session, provisional, resources, fiber, cancel, preferences)
    return document, fiber, result.asset, attachment


def route_created(
    session: Any, document: Any, resources: Any, fiber: Any, cancel: Any, preferences: Any
) -> Any:
    inputs = (session.engine, document, resources, fiber, cancel.handle)
    policy = (preferences.routing_backend, preferences.fiber_propagation)
    return curve_evaluation.evaluate_item(*inputs, *policy)


def publish(session: Any, request: Request, origin: int, payload: Any) -> None:
    document, _, _, _ = payload
    ports = inputs(document, request)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Fiber placement surfaces changed before publication.")
    restart = partial(enqueue, session, request, origin)
    fiber_tasks.publish_ready(session, origin, payload, ports, restart)
