"""Confirmed placements are cancellable authored work belonging to the gesture's undo step."""

from functools import partial
from typing import Any, cast

from anthroforge.core.construction import Curve
from anthroforge.core.jobs import Job
from anthroforge.core.junctions import members
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import (
    authored_jobs,
    dependencies,
    dependent_tasks,
    junction_edits,
    object_operations,
    object_revisions,
    placement_inputs,
    snap_edits,
    surface_providers,
)
from .evaluation_results import accepted_result


def confirm(
    session: Any,
    components: Any,
    targets: Any,
    origin: Any,
    direction: Any,
    offset: float = 0,
    anchor: Any = None,
) -> str:
    request = request_data(components, targets, origin, direction, offset, anchor)
    validate_components(session, request["components"])
    return begin(session, request)


def confirm_samples(session: Any, curve: str, projection: Any) -> str:
    item = object_operations.editable(session, curve)
    if not isinstance(item, Curve):
        raise ValueError("Sample placement requires a curve.")
    from .placement_inputs import validated

    data = validated(projection, len(item.points))
    if data is None:
        return ""
    refs = tuple(dict(curve=curve, point=p.id, part="position") for p in item.points)
    request = dict(components=refs, targets=data["targets"], samples=data["queries"])
    return begin(session, request)


def begin(session: Any, request: Any) -> str:
    request = dict(request, authored=authored_inputs(session.document, request))
    return authored_jobs.begin(session, partial(enqueue, session, request))


def authored_inputs(document: Any, request: Any) -> tuple[Any, ...]:
    return tuple(
        (key, document.object(key).construction_revision, document.object(key).pose_revision)
        for key in sorted(owners(document, request))
        if key in document.registry.records
    )


def validate_components(session: Any, refs: Any) -> None:
    for ref in refs:
        item = object_operations.editable(session, ref["curve"])
        if not isinstance(item, Curve) or ref["part"] not in ("position", "left", "right"):
            raise ValueError("Confirmed curve snapping requires editable curve components.")
        junction_edits.point(item, ref["point"])


def request_data(
    components: Any, targets: Any, origin: Any, direction: Any, offset: float, anchor: Any
) -> Any:
    if not components:
        raise ValueError("Confirmed curve placement needs selected components.")
    refs = tuple(dict(curve=r["curve"], point=r["point"], part=r["part"]) for r in components)
    return dict(
        components=refs,
        **placement_inputs.ray(targets, origin, direction, offset),
        anchor=anchor_reference(anchor, refs),
    )


def anchor_reference(anchor: Any, refs: Any) -> Any:
    selected = {key: anchor[key] for key in refs[0]} if anchor is not None else refs[0]
    if selected not in refs:
        raise ValueError("The snap anchor must be one of the selected curve components.")
    return selected


def owners(document: Any, request: Any) -> set[str]:
    result = {r["curve"] for r in request["components"]}
    for links in members(document.objects).values():
        if any(ref.curve in result for ref in links):
            result.update(ref.curve for ref in links)
    return result


def inputs(document: Any, request: Any) -> set[Port]:
    seeds = surface_providers.ports(document, request["targets"])
    seeds |= {Port(key, stage) for key in owners(document, request) for stage in ("path", "pose")}
    return dependencies.closure(dependencies.graph(document), seeds)


def enqueue(session: Any, request: Any, origin: int) -> str:
    if authored_inputs(session.document, request) != request["authored"]:
        return remember_pending(session, request, origin)
    job = make_job(session, request, origin)
    job.publish = partial(publish, session, request, origin, source=job.id)
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, request, origin)
    job.restart_on_input_change = True
    job.observes = frozenset(inputs(session.document, request))
    job.prerequisites = frozenset(surface_providers.ports(session.document, request["targets"]))
    job.reads = frozenset(p.owner for p in job.observes)
    job.workload = lambda _: Workload(affected=len(job.outputs), candidates=len(request["targets"]))
    return cast(str, session.scheduler.submit(job))


def remember_pending(session: Any, request: Any, origin: int) -> str:
    replay = partial(enqueue, session, request, origin)
    for entry in authored_jobs.affected(session, origin):
        if authored_inputs(entry.document, request) == request["authored"]:
            entry.pending_authored[origin] = replay
    return ""


def make_job(session: Any, request: Any, origin: int) -> Job:
    return Job(
        "Confirm exterior surface placement",
        frozenset(owners(session.document, request)),
        lambda document: snap_edits.Context(session.engine, document, session.resources.snapshot()),
        partial(compute, request),
        partial(publish, session, request, origin),
        key="surface_snap:" + ":".join(sorted(owners(session.document, request))),
        kind="surface_snap",
    )


def compute(request: Any, context: snap_edits.Context, cancel: Any) -> Any:
    return context.document, snap_edits.evaluate(context, request, cancel.handle)


def publish(session: Any, request: Any, origin: int, output: Any, source: str = "") -> None:
    document, changes = output
    sample = next(iter(changes.values()))
    proof = accepted_result(document, sample, inputs(document, request), "")
    before = session.document
    capture = authored_jobs.Capture(proof.inputs, partial(enqueue, session, request, origin))
    authored_jobs.publish(session, origin, partial(snap_edits.merge, changes=changes), capture)
    propagate_changes(session, before, changes, source)


def propagate_changes(session: Any, before: Any, changes: Any, source: str) -> None:
    ports = set().union(
        *(
            object_revisions.changed_ports(before.object(key), session.document.object(key))
            for key in changes
        )
    )
    session.scheduler.invalidate_ports(ports, source=source)
    dependent_tasks.changed(session, ports, published=False)
