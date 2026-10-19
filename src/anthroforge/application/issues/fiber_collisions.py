"""Read-only accepted-fiber collision evidence; authored curves never reroute implicitly."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.object_registry import kind
from anthroforge.core.results import Port, geometry_asset
from anthroforge.native import path_collisions
from anthroforge.native.mesh import NativeCancellation

from .. import attachment_assets, curve_sources, dependencies, routing_evaluation
from ..construction_policy import revisions
from .providers import Provider

NAME = "fiber_collisions.v1"
FIELDS = {
    "@membership",
    "matrix",
    "geometry_offset",
    "result",
    "parent",
    "follow",
    "engine_settings",
}


def fibers(document: Any) -> list[Fiber]:
    return [
        o
        for o in document.objects
        if isinstance(o, Fiber) and o.engine != "ROUTED" and o.result.asset
    ]


def surfaces(document: Any) -> tuple[str, ...]:
    return tuple(e.id for e in document.entities if geometry_asset(e))


def scopes(document: Any) -> set[str]:
    return {"document"} if fibers(document) else set()


def affected(document: Any, changes: Any) -> set[str]:
    values = (*changes.entities.values(), *changes.controls.values(), *changes.objects.values())
    return {"document"} if any(FIELDS & fields for fields in values) else set()


def source(document: Any, scope: str) -> Any:
    items = fibers(document)
    seeds = {Port(item.id, "pose") for item in items}
    seeds.update(Port(key, output) for key in surfaces(document) for output in ("pose", "geometry"))
    ports = dependencies.closure(dependencies.graph(document), seeds)
    return dict(
        paths=[(item.id, item.result.asset, item.result.status) for item in items],
        inputs=[asdict(value) for value in revisions(document, ports)],
    )


@dataclass(frozen=True)
class Context:
    document: Any
    resources: Any
    engine: Any


def provider(session: Any) -> Provider:
    return Provider(
        NAME,
        scopes,
        affected,
        source,
        check,
        lambda document: Context(document, session.resources.snapshot(), session.engine),
        lambda: NativeCancellation(session.engine),
    )


def check(context: Any, scope: str, cancel: Any) -> tuple[Issue, ...]:
    items, targets = fibers(context.document), surfaces(context.document)
    if not items or not targets:
        return ()
    collisions, tolerance = query(context, items, targets, cancel.handle)
    stamp = fingerprint(source(context.document, scope))
    return tuple(
        finding(context, item, targets[i], int(segment), tolerance, stamp)
        for item, result in zip(items, collisions, strict=True)
        for i, segment in enumerate(result)
        if segment >= 0
    )


def query(context: Context, items: list[Fiber], targets: tuple[str, ...], cancel: int) -> Any:
    handles, frames = attachment_assets.surface_inputs(
        context.engine, context.document, context.resources.meshes, targets
    )
    rows = [input_row(context, item, targets) for item in items]
    return path_collisions.check(context.engine, rows, handles, frames, cancel)


def input_row(
    context: Context, item: Fiber, targets: tuple[str, ...]
) -> path_collisions.CollisionPath:
    asset = context.resources.paths[item.result.asset]
    frame = curve_sources.world(context.engine, context.document, item.id)
    owners = routing_evaluation.owners(asset.authored, targets)
    return path_collisions.row(asset.path, frame, owners)


def finding(
    context: Context, item: Fiber, target: str, segment: int, tolerance: float, stamp: str
) -> Issue:
    parent = context.document.entity(target)
    return Issue(
        NAME,
        "document",
        "FIBER_COLLISION",
        "Fiber intersects " + parent.name,
        **finding_identity(item, target, stamp),
        evidence=collision_evidence(item, parent, segment, tolerance),
    )


def finding_identity(item: Fiber, target: str, stamp: str) -> dict[str, Any]:
    return dict(
        target=item.id,
        kind=kind(item),
        stage="collision",
        source=stamp,
        related=(target,),
        local_key=item.id + ":" + target,
        details="Accepted path intersects the surface. Authored shape and engine are unchanged.",
    )


def collision_evidence(item: Fiber, parent: Any, segment: int, tolerance: float) -> str:
    return evidence(
        segment=segment,
        tolerance_metres=tolerance,
        path=item.result.asset,
        surface=geometry_asset(parent),
        pending=item.result.status == "pending",
    )
