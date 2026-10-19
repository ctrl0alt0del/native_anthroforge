"""Scene-membership invalidation shares ordinary path jobs and revision contracts."""

from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.results import Port


def changed(session: Any, before: Any) -> None:
    from . import path_tasks

    previous = before.index.structure.dependencies.routing_scene
    if previous == session.document.index.structure.dependencies.routing_scene:
        return
    existing = before.registry.construction
    ports = {
        Port(o.id, "routing_scope")
        for o in session.document.objects
        if isinstance(o, Curve) and o.id in existing
    }
    session.scheduler.invalidate_ports(ports, reason="routing_scene_membership_changed")
    path_tasks.edited(session, ports)
