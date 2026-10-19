"""Engine-specific cost policy, independent of shared queue and publication contracts."""

from typing import Any

from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.fibers import Fiber
from anthroforge.core.routing_obstacles import references
from anthroforge.core.scheduling import Workload

from .surface_providers import triangle_count


def kind(item: Any) -> str:
    if isinstance(item.engine_settings, RoutingSettings):
        return "curve_routing"
    return "fiber_path" if isinstance(item, Fiber) else "curve_path"


def workload(session: Any, item: Any, document: Any) -> Workload:
    if not isinstance(item.engine_settings, RoutingSettings):
        from .fiber_tasks import path_workload

        return path_workload(session, item, document)
    return routing_workload(session, item, document)


def routing_workload(session: Any, item: Any, document: Any) -> Workload:
    surfaces = references(document, item)
    triangles = sum(triangle_count(document, session.assets, key) for key in surfaces)
    return Workload(
        affected=1,
        entities=len(surfaces),
        candidates=item.engine_settings.samples,
        triangles=triangles,
    )
