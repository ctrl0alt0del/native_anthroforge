"""Skin authoring uses the ordinary document transaction boundary."""

import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.skin import EnvelopeSettings, Skin, SkinContributor
from anthroforge.core.tissues import TissueVCP

from . import object_operations, skin_builder_configuration, skin_configuration_operations

if TYPE_CHECKING:
    from .session import Session

SECTIONS = ("draft_settings", "envelope_settings", "topology_settings", "deformation_settings")


def update_mode(session: "Session", mode: str) -> None:
    skin = session.document.skin
    updated = replace(skin, update_mode=mode)
    if updated != skin:
        session.replace_document(skin=updated)


def reset_envelope(session: "Session") -> None:
    configure(session, "envelope_settings", asdict(EnvelopeSettings()))


def import_draft_plan(session: "Session", path: str) -> None:
    plan = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(plan, dict):
        raise ValueError("Expected an AVBD draft plan object.")
    configure(session, "draft_settings", {"plan": plan})


def effective_settings(document: Any, owner: str) -> Any:
    return skin_builder_configuration.effective(document.skin, owner, document.object(owner).name)


def configure(session: "Session", section: str, values: dict[str, Any]) -> None:
    validate_section(section, values)
    skin = session.document.skin
    if section in ("draft_settings", "envelope_settings"):
        configure_builder(session, section, values)
        return
    settings = replace(getattr(skin, section), **setting_values(values))
    if settings == getattr(skin, section):
        return
    rebuild = section != "deformation_settings" or bool(set(values) - {"method"})
    session.replace_document(skin=invalidate(skin, rebuild, **{section: settings}))
    if section == "deformation_settings":
        request_update(session)


def configure_builder(session: "Session", section: str, values: dict[str, Any]) -> None:
    skin = session.document.skin
    updated = skin_configuration_operations.configure(skin, section, values)
    if updated != skin:
        session.replace_document(skin=skin_configuration_operations.changed(skin, updated))


def request_update(session: "Session") -> None:
    from . import skin_update_tasks

    skin_update_tasks.pending(session)


def validate_section(section: str, values: dict[str, Any]) -> None:
    if section not in SECTIONS:
        raise ValueError("Unknown skin settings section.")
    if section == "draft_settings" and "backend" in values:
        from .skin_evaluation import BUILDERS

        if values["backend"] not in BUILDERS:
            raise ValueError(f"Unknown draft skin builder: {values['backend']}")


def setting_values(values: dict[str, Any]) -> dict[str, Any]:
    if isinstance(values.get("plan"), dict):
        values = values | {"plan": json.dumps(values["plan"], allow_nan=False)}
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
    updated, common = skin_builder_configuration.contributor(skin, owner, values)
    if common:
        previous = settings_for(skin, owner)
        changed = change_settings(previous, common)
        rows = {row.owner: row for row in skin.contributors} | {owner: changed}
        updated = replace(updated, contributors=tuple(rows.values()))
    if updated != skin:
        changed_skin = skin_configuration_operations.changed(skin, updated)
        session.replace_document(skin=invalidate(updated, True) if common else changed_skin)


def change_settings(previous: SkinContributor, values: dict[str, Any]) -> SkinContributor:
    return replace(previous, **values)


def settings_for(skin: Skin, owner: str) -> SkinContributor:
    return next((row for row in skin.contributors if row.owner == owner), SkinContributor(owner))


def require_contributor(session: "Session", owner: str, values: dict[str, Any]) -> None:
    if "owner" in values or "painted" in values:
        raise ValueError("Contributor identity and painted resources use dedicated operations.")
    if owner in session.document.index.entities:
        require_scp_settings(session, owner, values)
        return
    item = object_operations.editable(session, owner)
    require_construction_settings(item, values)
    if values.get("flow") and isinstance(item, Fiber) and item.closed:
        raise ValueError("Closed Fibers are loop guides; FLOW requires an open Fiber.")


def require_scp_settings(session: "Session", owner: str, values: dict[str, Any]) -> None:
    session.editable(owner)
    if values.get("limb") is not None and not session.document.index.entities[owner].parent:
        raise ValueError("A limb starts at a child SCP attachment.")
    if "flow" in values:
        raise ValueError("FLOW guides require a Fiber.")
    if "fiber_radius" in values:
        raise ValueError("Fiber skin radius is no longer supported.")


def require_construction_settings(item: Any, values: dict[str, Any]) -> None:
    if not isinstance(item, (Fiber, TissueVCP)):
        raise ValueError("Skin contributors must be SCPs, tissues or fibers.")
    if isinstance(item, Fiber) and set(values) - {"flow"}:
        raise ValueError("Fibers support topology FLOW only; not physical skin settings.")
    if set(values) - {"gap_mode", "gap_limit_ratio", "gap_strength", "flow"}:
        raise ValueError("Collagen and subtree density require an SCP.")
    if "flow" in values and not isinstance(item, Fiber):
        raise ValueError("FLOW guides require a Fiber.")


def inspect(session: "Session") -> dict[str, Any]:
    return asdict(session.document.skin)


def report(session: "Session") -> dict[str, Any]:
    from . import skin_reports

    return skin_reports.describe(session)
