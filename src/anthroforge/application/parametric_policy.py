"""Formula-owned coordinates and topology restrictions are shared by every editor."""

from typing import Any

from anthroforge.core.construction import Curve
from anthroforge.core.parametric import ParametricSettings


def require_change(document: Any, before: Any, after: Any) -> None:
    if not isinstance(before, Curve) or not isinstance(after, Curve):
        return
    if before.engine == after.engine == "PARAMETRIC":
        if coordinates(before) != coordinates(after):
            raise ValueError(
                "Parametric point positions and handles are controlled by XYZ expressions."
            )
        old, new = before.engine_settings, after.engine_settings
        if (
            isinstance(old, ParametricSettings)
            and isinstance(new, ParametricSettings)
            and old.resolution != new.resolution
        ):
            require_resolution(document, before)


def coordinates(item: Curve) -> tuple[Any, ...]:
    return tuple(
        (p.id, p.position, p.left, p.right, p.left_mode, p.right_mode) for p in item.points
    )


def require_resolution(document: Any, item: Curve) -> None:
    from .construction_policy import require_topology_edit

    if any(p.junction for p in item.points):
        raise ValueError("Parametric resolution is locked while the curve has a junction.")
    require_topology_edit(document, item.id)


def readonly(item: Any, path: tuple[str, ...]) -> str:
    if not isinstance(item, Curve) or item.engine != "PARAMETRIC":
        return ""
    if path[0] == "points" and path[-1] in ("position", "left", "right"):
        return "Position is controlled by the Parametric XYZ expressions."
    config = item.engine_settings
    if isinstance(config, ParametricSettings) and path[:2] == ("engine_settings", "interval"):
        if path[-1] in ("start", "end") and getattr(config.interval, path[-1] + "_expression"):
            return "This interval endpoint is controlled by its expression."
    return ""
