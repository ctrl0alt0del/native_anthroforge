"""Engine-specific cost policy, independent of shared queue and publication contracts."""

from typing import Any

from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import geometry_asset
from anthroforge.core.routing_obstacles import targets
from anthroforge.core.scheduling import Workload


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
    surfaces = targets(document, item)
    triangles = sum(
        session.assets[geometry_asset(document.entity(key))].mesh.counts[3]
        for key in surfaces
        if geometry_asset(document.entity(key)) in session.assets
    )
    return Workload(
        affected=1,
        entities=len(surfaces),
        candidates=item.engine_settings.samples,
        triangles=triangles,
    )
