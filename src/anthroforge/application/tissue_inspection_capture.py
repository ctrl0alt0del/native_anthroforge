"""Validate frozen tissue presentation at the shared inspection-export boundary."""

from typing import Any

from . import tissue_inspection as inspection
from . import tissue_inspection_stages as stages


def capture(session: Any, selected: str, settings: Any) -> dict[str, Any]:
    if not settings:
        return {}
    stage, reference = settings.get("stage", ""), settings.get("reference", "")
    mode = settings.get("mode", "Overlay")
    validate(session, selected, stage, reference, mode)
    return dict(
        stage=stage,
        reference=reference,
        mode=mode,
        point=point(session, selected, stage),
        finding=finding(session, selected, settings),
    )


def validate(session: Any, selected: str, stage: str, reference: str, mode: str) -> None:
    item = stages.tissue(session, selected)
    if mode not in ("Overlay", "Displacement"):
        raise ValueError("Unknown tissue comparison presentation.")
    for key in (stage, reference):
        if key and not stages.row(session, item, key)["available"]:
            raise ValueError("The requested inspection stage is unavailable.")
    if mode == "Displacement" and stage and reference:
        stages.compatible(item, reference, stage)


def point(session: Any, selected: str, stage: str) -> dict[str, Any]:
    value = inspection.status(session, "point")
    if value["state"] == "ready" and value["target"] == selected:
        report = value["report"]
        if stage == report["stage"] or (
            not stage and report["asset"] == stages.tissue(session, selected).result.asset
        ):
            return dict(report)
    return {}


def finding(session: Any, selected: str, settings: Any) -> dict[str, Any]:
    if not settings.get("finding"):
        return {}
    session.issues.listening.discover_changes()
    row = session.issues.presentation.get(settings["finding"])
    if row["freshness"] != "current" or row["target"] != selected:
        raise ValueError("The finding changed. Check geometry before exporting this view.")
    if row["stage"] != settings.get("stage"):
        raise ValueError("The displayed stage must match the finding being exported.")
    return dict(row)
