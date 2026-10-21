"""Per-part authoring uses shared capability, reference and transaction policies."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core import tissue_parts
from anthroforge.core.tissue_settings import HeightSmoothing, SectionProfile
from anthroforge.native import tissue_parts as native

from . import tissue_operations, tissue_strategy_operations
from .construction_codec import tuples


def selected(item: Any, part: str) -> Any:
    value = next((p for p in tissue_parts.active(item) if p.id == part), None)
    if value is None:
        raise ValueError("Choose an accepted material part.")
    return value


def copy_side(
    session: Any,
    target: str,
    source: str,
    destination: str,
    part: str = "main",
    all_parts: bool = False,
) -> None:
    item = tissue_operations.tissue(session, target)
    parts = copied_sides(item, source, destination, part, all_parts)
    updated = replace(item, parts=tissue_parts.installed(item, parts))
    tissue_operations.install_inflation(session, item, updated)


def copied_sides(item: Any, source: str, destination: str, part: str, all_parts: bool) -> Any:
    if {source, destination} != {"a", "b"} or type(all_parts) is not bool:
        raise ValueError("Copy requires opposite sides A/B and a Boolean all_parts flag.")
    selected(item, part)
    return tuple(
        replace(p, **{destination: getattr(p, source)}) if all_parts or p.id == part else p
        for p in tissue_parts.active(item)
    )


def connector(session: Any, target: str, part: str, width: float, fullness: float) -> None:
    item = tissue_operations.tissue(session, target)
    if part == "main":
        raise ValueError("Connector settings belong to a branch part.")
    changed = replace(selected(item, part), connector_width=width, connector_fullness=fullness)
    parts = tuple(changed if p.id == part else p for p in tissue_parts.active(item))
    tissue_strategy_operations.install(
        session, replace(item, parts=tissue_parts.installed(item, parts))
    )


def profile_value(session: Any, depth: float) -> dict[str, Any]:
    values = native.reset_profile(session.engine, depth)
    return asdict(SectionProfile(values[:4], values[4:8], values[8], initialized=True))


def initialize(session: Any, item: Any, changes: Any, part: str, side: str) -> Any:
    current = getattr(selected(item, part), side).inflation
    if (
        changes.get("mode") == "SECTION_PROFILE"
        and not current.profile.initialized
        and "profile" not in changes
    ):
        return dict(changes, profile=profile_value(session, changes.get("amount", current.amount)))
    if "profile" in changes:
        return dict(changes, profile=dict(changes["profile"], initialized=True))
    return changes


def profile_reset(session: Any, target: str, part: str = "main", side: str = "a") -> None:
    item = tissue_operations.tissue(session, target)
    if side not in ("a", "b"):
        raise ValueError("Choose side A or B.")
    depth = getattr(selected(item, part), side).inflation.amount
    tissue_operations.inflation(
        session, target, dict(profile=profile_value(session, depth)), part, side
    )


def profile_scale(
    session: Any, target: str, factor: float, part: str = "main", side: str = "a"
) -> None:
    item = tissue_operations.tissue(session, target)
    if side not in ("a", "b"):
        raise ValueError("Choose side A or B.")
    previous = getattr(selected(item, part), side).inflation.profile
    profile = scaled_profile(session, asdict(previous), factor)
    tissue_operations.inflation(session, target, dict(profile=profile), part, side)


def scaled_profile(session: Any, profile: dict[str, Any], factor: float) -> dict[str, Any]:
    previous = SectionProfile(**tuples(profile))
    depths = native.scale_profile(session.engine, previous.depths, factor)
    return asdict(replace(previous, depths=depths, initialized=True))


def control_reset(session: Any, target: str, part: str = "main", side: str = "a") -> None:
    item = tissue_operations.tissue(session, target)
    point = control_value(session, item, part)
    tissue_operations.inflation(session, target, dict(control=point), part, side)


def control_value(session: Any, item: Any, part: str) -> Any:
    selected(item, part)
    index = item.base_state.parts.index(part)
    mesh = session.assets[item.base_result.asset].mesh
    return native.default_control(mesh, index)


def smoothing(session: Any, target: str, changes: Any, part: str = "main", side: str = "a") -> None:
    item = tissue_operations.tissue(session, target)
    if side not in ("a", "b") or set(changes) - set(HeightSmoothing.__dataclass_fields__):
        raise ValueError("Choose side A/B and supported height smoothing settings.")
    current = selected(item, part)
    previous = getattr(current, side)
    edited = replace(previous, smoothing=replace(previous.smoothing, **changes))
    changed = replace(current, **{side: edited})
    parts = tuple(changed if p.id == part else p for p in tissue_parts.active(item))
    tissue_strategy_operations.install(
        session, replace(item, parts=tissue_parts.installed(item, parts))
    )
