"""Surface inputs declared by path engines and anatomical binding capabilities."""

from .construction import Curve
from .curve_engines import RoutingSettings
from .fibers import Fiber
from .results import Port


def targets(item: Curve) -> set[str]:
    settings = item.engine_settings
    result = (
        set(settings.obstacles)
        if isinstance(settings, RoutingSettings) and settings.obstacle_mode == "MANUAL"
        else set()
    )
    if isinstance(item, Fiber):
        result.update(item.supports)
        result.update(binding.target for binding in item.bindings)
        if item.edit:
            result.update(item.edit.candidates)
    return result


def inputs(item: Curve) -> set[Port]:
    if not isinstance(item, Fiber) and not isinstance(item.engine_settings, RoutingSettings):
        return set()
    scope = {Port(item.id, "routing_scope")} if item.engine == "ROUTED" else set()
    return (
        scope
        | {Port(item.id, "pose")}
        | {Port(target, role) for target in targets(item) for role in ("geometry", "pose")}
    )
