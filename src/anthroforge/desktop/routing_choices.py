"""Routing-policy descriptions for optional editors; no geometry or selection policy in QML."""

from collections import OrderedDict
from dataclasses import replace

from anthroforge.core import anatomical_surfaces, routing_obstacles
from anthroforge.core.construction import Curve
from anthroforge.core.curve_constraints import required_points
from anthroforge.core.curve_dependencies import targets as explicit_targets
from anthroforge.core.curve_engines import RoutingSettings, decode


class RoutingChoices:
    """Reuse descriptions across result/pose publications; retain only eight structural graphs."""

    def __init__(self):
        self.entries = OrderedDict()

    def rows(self, document, key, settings):
        graph = document.index.structure.dependencies
        signature = choice_signature(document, key, settings)
        if signature not in self.entries:
            self.entries[signature] = graph, obstacle_rows(document, key, settings)
            if len(self.entries) > 8:
                self.entries.popitem(last=False)
        self.entries.move_to_end(signature)
        return self.entries[signature][1]


def choice_signature(document, key, settings):
    return (
        id(document.index.structure.dependencies),
        key,
        settings.get("obstacle_mode", "AUTO"),
        tuple(settings.get("obstacles", ())),
        tuple(settings.get("excluded_obstacles", ())),
        tuple((item.id, item.name, item.parent) for item in document.registry.anatomy.values()),
    )


def point_rows(document, key):
    curve = document.registry.construction.get(key)
    if not isinstance(curve, Curve):
        return []
    required = required_points(curve)
    return [point_row(p, i, required) for i, p in enumerate(curve.points)]


def point_row(point, index, required):
    reason = required.get(point.id, "")
    return dict(
        key=point.id,
        label=f"Point {index + 1}",
        detail=reason or "Authored routing point",
        reason=reason,
        locked=bool(reason),
        chosen=True,
    )


def obstacle_rows(document, key, settings):
    curve = document.registry.construction.get(key)
    if not isinstance(curve, Curve):
        return []
    candidate = replace(curve, engine_settings=decode("ROUTED", settings))
    graph = routing_obstacles.graph(document, candidate)
    rejected = graph.routing_excluded.get(key, ())
    required = explicit_targets(replace(candidate, engine_settings=RoutingSettings()))
    return [
        obstacle_row(
            document, document.object(ref.target), candidate.engine_settings, rejected, required
        )
        for ref in anatomical_surfaces.defaults(document.entities, document.objects)
    ]


def obstacle_row(document, item, settings, rejected, required):
    automatic = settings.obstacle_mode == "AUTO"
    reason = "Required binding/support" if item.id in required else ""
    if item.id in rejected:
        reason = "Excluded automatically: geometry depends on this path"
    chosen = item.id in (settings.excluded_obstacles if automatic else settings.obstacles)
    if reason:
        chosen = item.id in rejected if automatic else item.id in required
    return choice_row(item, hierarchy(document, item), chosen, reason)


def choice_row(item, detail, chosen, reason):
    return dict(
        key=item.id,
        label=item.name,
        detail=detail,
        chosen=chosen,
        locked=bool(reason),
        reason=reason,
    )


def hierarchy(document, item):
    names, current = [], item
    while current.parent:
        current = document.object(current.parent)
        names.append(current.name)
    path = " / ".join(reversed(names)) or "Anatomy root"
    return f"{path} · {item.id[:8]}"
