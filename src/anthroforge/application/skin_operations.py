"""Skin authoring uses the ordinary document transaction boundary."""

from dataclasses import asdict, replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.skin import Skin, SkinContributor
from anthroforge.core.tissues import TissueVCP

from . import object_operations

if TYPE_CHECKING:
    from .session import Session

SECTIONS = ("envelope_settings", "topology_settings", "deformation_settings")


def configure(session: "Session", section: str, values: dict[str, Any]) -> None:
    if section not in SECTIONS:
        raise ValueError("Unknown skin settings section.")
    skin = session.document.skin
    settings = replace(getattr(skin, section), **setting_values(values))
    if settings == getattr(skin, section):
        return
    rebuild = section != "deformation_settings" or bool(set(values) - {"method"})
    session.replace_document(skin=invalidate(skin, rebuild, **{section: settings}))


def setting_values(values: dict[str, Any]) -> dict[str, Any]:
    return {
        key: tuple(value) if key in ("plane_origin", "plane_normal") else value
        for key, value in values.items()
    }


def invalidate(skin: Skin, rebuild: bool, **changes: Any) -> Skin:
    return replace(
        skin,
        **changes,
        revision=skin.revision + 1,
        final=replace(skin.final, status="pending") if skin.final.asset else skin.final,
        construction_stale=skin.construction_stale or bool(skin.topology.asset and rebuild),
    )


def contributor(session: "Session", owner: str, values: dict[str, Any]) -> None:
    require_contributor(session, owner, values)
    skin = session.document.skin
    previous = settings_for(skin, owner)
    changed = replace(previous, **values)
    if changed == previous and any(row.owner == owner for row in skin.contributors):
        return
    rows = {row.owner: row for row in skin.contributors} | {owner: changed}
    session.replace_document(skin=invalidate(skin, True, contributors=tuple(rows.values())))


def settings_for(skin: Skin, owner: str) -> SkinContributor:
    return next((row for row in skin.contributors if row.owner == owner), SkinContributor(owner))


def require_contributor(session: "Session", owner: str, values: dict[str, Any]) -> None:
    if "owner" in values or "painted" in values:
        raise ValueError("Contributor identity and painted resources use dedicated operations.")
    if owner in session.document.index.entities:
        session.editable(owner)
        if {"flow", "fiber_radius"} & values.keys():
            raise ValueError("FLOW guides and fiber radius require a Fiber.")
        return
    item = object_operations.editable(session, owner)
    require_construction_settings(item, values)


def require_construction_settings(item: Any, values: dict[str, Any]) -> None:
    if not isinstance(item, (Fiber, TissueVCP)):
        raise ValueError("Skin contributors must be SCPs, tissues or fibers.")
    if set(values) - {"gap_mode", "gap_limit_ratio", "gap_strength", "flow", "fiber_radius"}:
        raise ValueError("Collagen and subtree density require an SCP.")
    if {"flow", "fiber_radius"} & values.keys() and not isinstance(item, Fiber):
        raise ValueError("FLOW guides and fiber radius require a Fiber.")


def inspect(session: "Session") -> dict[str, Any]:
    return asdict(session.document.skin)
