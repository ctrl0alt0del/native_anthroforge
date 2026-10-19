"""Per-part authoring uses shared capability, reference and transaction policies."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core import tissue_parts
from anthroforge.core.tissue_settings import SectionProfile
from anthroforge.native import tissue_parts as native

from . import tissue_operations, tissue_strategy_operations


def selected(item: Any, part: str) -> Any:
    value = next((p for p in tissue_parts.active(item) if p.id == part), None)
    if value is None:
        raise ValueError("Choose an accepted material part.")
    return value


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


def control_reset(session: Any, target: str, part: str = "main", side: str = "a") -> None:
    item = tissue_operations.tissue(session, target)
    selected(item, part)
    index = item.base_state.parts.index(part)
    mesh = session.assets[item.base_result.asset].mesh
    point = native.default_control(mesh, index)
    tissue_operations.inflation(session, target, dict(control=point), part, side)
