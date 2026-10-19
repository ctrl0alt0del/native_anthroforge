"""Read-only accepted-fiber collision evidence; authored curves never reroute implicitly."""

from dataclasses import asdict, dataclass
from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.fibers import Fiber
from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.object_registry import kind
from anthroforge.core.results import Port
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native import path_collisions
from anthroforge.native.mesh import NativeCancellation

from .. import curve_sources, dependencies, surface_providers
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
    "final_result",
    "base_result",
}


def fibers(document: Any) -> list[Fiber]:
    return [
        o
        for o in document.objects
        if isinstance(o, Fiber) and o.engine != "ROUTED" and o.result.asset
    ]


def surfaces(document: Any) -> tuple[SurfaceReference, ...]:
    defaults = anatomical_surfaces.defaults(document.entities, document.objects)
    bound = {b.reference for f in fibers(document) for b in f.bindings}
    return tuple(sorted(set(defaults) | bound))


def scopes(document: Any) -> set[str]:
    return {"document"} if fibers(document) else set()


def affected(document: Any, changes: Any) -> set[str]:
    values = (*changes.entities.values(), *changes.controls.values(), *changes.objects.values())
    return {"document"} if any(FIELDS & fields for fields in values) else set()


def source(document: Any, scope: str) -> Any:
    items = fibers(document)
    seeds = {Port(item.id, "pose") for item in items}
    seeds.update(surface_providers.ports(document, surfaces(document)))
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
    items = fibers(context.document)
    stamp = fingerprint(source(context.document, scope))
    targets, unavailable = available(context, stamp)
    if not items or not targets:
        return unavailable
    collisions, tolerance = query(context, items, targets, cancel.handle)
    return unavailable + tuple(
        finding(context, item, (targets[i], int(segment)), tolerance, stamp)
        for item, result in zip(items, collisions, strict=True)
        for i, segment in enumerate(result)
        if segment >= 0
    )


def available(context: Context, stamp: str) -> tuple[Any, tuple[Issue, ...]]:
    accepted, issues = [], []
    for ref in surfaces(context.document):
        try:
            provider = surface_providers.snapshot(
                context.engine, context.document, context.resources.meshes, ref
            )
            if provider.resource.mesh.counts[3]:
                accepted.append(ref)
        except ValueError as error:
            issues.append(unavailable_surface(context.document, ref, stamp, str(error)))
    return tuple(accepted), tuple(issues)


def unavailable_surface(document: Any, ref: SurfaceReference, stamp: str, reason: str) -> Issue:
    item = document.object(ref.target)
    return Issue(
        NAME,
        "document",
        "COLLISION_SURFACE_UNAVAILABLE",
        "Collision check unavailable on " + item.name,
        target=item.id,
        kind=kind(item),
        stage="collision",
        source=stamp,
        details=reason,
        local_key=item.id + ":" + ref.role,
        evidence=evidence(surface_role=ref.role),
    )


def query(
    context: Context, items: list[Fiber], targets: tuple[SurfaceReference, ...], cancel: int
) -> Any:
    handles, frames = surface_providers.inputs(
        context.engine, context.document, context.resources.meshes, targets
    )
    rows = [input_row(context, item, targets) for item in items]
    return path_collisions.check(context.engine, rows, handles, frames, cancel)


def input_row(
    context: Context, item: Fiber, targets: tuple[SurfaceReference, ...]
) -> path_collisions.CollisionPath:
    asset = context.resources.paths[item.result.asset]
    frame = curve_sources.world(context.engine, context.document, item.id)
    bindings = {
        b.point: targets.index(b.reference) + 1
        for b in asset.authored.bindings
        if b.reference in targets
    }
    owners = tuple(bindings.get(p.id, 0) for p in asset.authored.points)
    return path_collisions.row(asset.path, frame, owners)


def finding(
    context: Context, item: Fiber, hit: tuple[SurfaceReference, int], tolerance: float, stamp: str
) -> Issue:
    target, segment = hit
    parent = context.document.object(target.target)
    return Issue(
        NAME,
        "document",
        "FIBER_COLLISION",
        "Fiber intersects " + parent.name,
        **finding_identity(item, target, stamp),
        evidence=collision_evidence(item, parent, target.role, segment, tolerance),
    )


def finding_identity(item: Fiber, target: SurfaceReference, stamp: str) -> dict[str, Any]:
    return dict(
        target=item.id,
        kind=kind(item),
        stage="collision",
        source=stamp,
        related=(target.target,),
        local_key=item.id + ":" + target.target + ":" + target.role,
        details="Accepted path intersects the surface. Authored shape and engine are unchanged.",
    )


def collision_evidence(item: Fiber, parent: Any, role: str, segment: int, tolerance: float) -> str:
    return evidence(
        segment=segment,
        tolerance_metres=tolerance,
        path=item.result.asset,
        surface=anatomical_surfaces.result(parent, role).asset,
        surface_role=role,
        pending=item.result.status == "pending",
    )
