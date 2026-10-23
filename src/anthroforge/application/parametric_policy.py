"""Formula-owned coordinates and topology restrictions are shared by every editor."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Curve, Deformer
from anthroforge.core.document import Document
from anthroforge.core.numeric_properties import NumericDescriptor
from anthroforge.core.parametric import ParametricSettings


def require_change(document: Document, before: Any, after: Any) -> None:
    if not isinstance(before, Curve) or not isinstance(after, Curve):
        return
    if before.engine == after.engine == "PARAMETRIC":
        if coordinates(before) != coordinates(after):
            raise ValueError(
                "Parametric point positions and handles are controlled by XYZ expressions."
            )
    if after.engine == "PARAMETRIC" and point_count(before) != point_count(after):
        require_resolution(document, before)


def point_count(item: Curve) -> int:
    config = item.engine_settings
    return config.resolution if isinstance(config, ParametricSettings) else len(item.points)


def coordinates(item: Curve) -> tuple[Any, ...]:
    return tuple(
        (p.id, p.position, p.left, p.right, p.left_mode, p.right_mode) for p in item.points
    )


def require_resolution(document: Document, item: Curve) -> None:
    reason = resolution_reason(document, item)
    if reason:
        raise ValueError(reason)


def resolution_reason(document: Document, item: Curve) -> str:
    from .construction_policy import topology_locks

    if any(p.junction for p in item.points):
        return "Resolution is locked while the curve has a junction; detach it to resize."
    reason = membership_reason(document, item.id) or formula_reason(document, item.id)
    if reason:
        return reason
    locks = topology_locks(document, item.id)
    return "Topology is locked: " + "; ".join(r["reason"] for r in locks) if locks else ""


def membership_reason(document: Document, curve: str) -> str:
    for owner in document.entities:
        for binding in owner.deformers:
            if binding.target.stage == "CURVE" and binding.target.component == curve:
                if point_membership(binding):
                    return (
                        "Resolution is locked by point membership or weights on "
                        + owner.name
                        + "; clear the assignment or remove its deformer binding to resize."
                    )
    return ""


def point_membership(binding: Deformer) -> bool:
    return bool(binding.indices or binding.members or binding.weights or binding.weighted_members)


def formula_reason(document: Document, curve: str) -> str:
    for driver in document.driving_shortcuts:
        for formula in driver.formulas:
            references = (formula.target, *(i.property for i in formula.inputs if i.property))
            if any(r.target == curve and r.path[0] == "points" for r in references):
                return (
                    "Resolution is locked by generated-point formula references in "
                    + driver.label
                    + "; remove or retarget those references to resize."
                )
    return ""


def descriptor(document: Document, value: NumericDescriptor) -> NumericDescriptor:
    if value.reference.path != ("engine_settings", "resolution"):
        return value
    item = document.object(value.reference.target)
    if not isinstance(item, Curve) or item.engine != "PARAMETRIC":
        return value
    reason = resolution_reason(document, item)
    return replace(value, writable=value.writable and not reason, reason=reason or value.reason)


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
