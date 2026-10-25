"""Conversion-time guide selection; evaluation never consults this user preference."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.curve_constraints import required_points


def point_ids(item: Curve, preference: str) -> tuple[str, ...]:
    if item.closed or preference == "ALL_POINTS":
        return tuple(p.id for p in item.points)
    required = required_points(item)
    return tuple(p.id for p in item.points if p.id in required)


def candidate(session: Any, item: Curve, engine: str, settings: Any) -> Curve:
    from .parametric_operations import switch

    if item.engine != engine and "PARAMETRIC" in (item.engine, engine):
        changed = switch(session, item, engine)
        if settings is not None:
            changed = configured(changed, engine, settings)
    else:
        changed = configured(item, engine, settings)
    if engine == "ROUTED" and item.engine != "ROUTED":
        selected = point_ids(changed, session.preferences.value.routing_conversion_points)
        changed = replace(changed, points=tuple(p for p in changed.points if p.id in selected))
    return changed


def configured(item: Curve, engine: str, settings: Any) -> Curve:
    from anthroforge.core.curve_engines import decode

    if settings is None:
        settings = {"samples": max(64, len(item.points))} if engine == "ROUTED" else {}
    return replace(item, engine_settings=decode(engine, settings))
