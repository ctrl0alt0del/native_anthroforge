"""Surface inputs declared by path engines and anatomical binding capabilities."""

from . import anatomical_surfaces
from .construction import Curve
from .curve_engines import RoutingSettings
from .fiber_support_policy import selected_targets
from .fibers import Fiber
from .results import Port
from .surface_references import SurfaceReference


def targets(item: Curve) -> set[str]:
    settings = item.engine_settings
    result = (
        set(settings.obstacles)
        if isinstance(settings, RoutingSettings) and settings.obstacle_mode == "MANUAL"
        else set()
    )
    if isinstance(item, Fiber):
        result.update(s.reference.target for s in item.supports)
        result.update(binding.target for binding in item.bindings)
        result.update(ref.target for ref in item.support_policy.included)
        if item.edit:
            result.update(r.target for r in edit_references(item))
    return result


def inputs(item: Curve, objects: tuple[object, ...] = ()) -> set[Port]:
    if not isinstance(item, Fiber) and not isinstance(item.engine_settings, RoutingSettings):
        return set()
    scope = {Port(item.id, "routing_scope")} if item.engine == "ROUTED" else set()
    refs = references(item, objects)
    return (
        scope
        | {Port(item.id, "pose")}
        | {anatomical_surfaces.port(ref) for ref in refs}
        | {Port(ref.target, "pose") for ref in refs}
    )


def references(item: Curve, objects: tuple[object, ...] = ()) -> set[SurfaceReference]:
    result = routing_references(item.engine_settings, objects)
    if isinstance(item, Fiber):
        result.update(s.reference for s in item.supports)
        result.update(b.reference for b in item.bindings)
        result.update(item.support_policy.included)
        if item.edit:
            result.update(edit_references(item))
    return result


def routing_references(settings: object, objects: tuple[object, ...]) -> set[SurfaceReference]:
    if not isinstance(settings, RoutingSettings) or settings.obstacle_mode != "MANUAL":
        return set()
    tissues = {r.target for r in anatomical_surfaces.defaults((), objects)}
    return {
        SurfaceReference(k, "TISSUE_FINAL" if k in tissues else "SCP_GEOMETRY")
        for k in settings.obstacles
    }


def edit_references(item: Fiber) -> set[SurfaceReference]:
    if item.edit is None:
        return set()
    searching = any(
        b.capture_scope == "ANY_PARENT" and b.attachment is not None and b.point in item.edit.rebind
        for b in item.bindings
    )
    if searching:
        return set(item.edit.candidates)
    parents = tuple(b.reference for b in item.bindings)
    return set(selected_targets(item.edit.candidates, parents, item.support_policy))
