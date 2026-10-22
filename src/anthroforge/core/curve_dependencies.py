"""Surface inputs declared by path engines and anatomical binding capabilities."""

from . import anatomical_surfaces
from .construction import Curve
from .curve_engines import RoutingSettings
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
        if item.edit:
            result.update(r.target for r in item.edit.candidates)
    return result


def inputs(item: Curve, objects: tuple[object, ...] = ()) -> set[Port]:
    if not isinstance(item, Fiber) and not isinstance(item.engine_settings, RoutingSettings):
        return set()
    scope = {Port(item.id, "routing_scope")} if item.engine == "ROUTED" else set()
    return (
        scope
        | {Port(item.id, "pose")}
        | {anatomical_surfaces.port(ref) for ref in references(item, objects)}
        | {Port(ref.target, "pose") for ref in references(item, objects)}
    )


def references(item: Curve, objects: tuple[object, ...] = ()) -> set[SurfaceReference]:
    result = routing_references(item.engine_settings, objects)
    if isinstance(item, Fiber):
        result.update(s.reference for s in item.supports)
        result.update(b.reference for b in item.bindings)
        if item.edit:
            result.update(item.edit.candidates)
    return result


def routing_references(settings: object, objects: tuple[object, ...]) -> set[SurfaceReference]:
    if not isinstance(settings, RoutingSettings) or settings.obstacle_mode != "MANUAL":
        return set()
    tissues = {r.target for r in anatomical_surfaces.defaults((), objects)}
    return {
        SurfaceReference(k, "TISSUE_FINAL" if k in tissues else "SCP_GEOMETRY")
        for k in settings.obstacles
    }
