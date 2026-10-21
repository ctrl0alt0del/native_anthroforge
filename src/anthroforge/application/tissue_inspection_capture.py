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
        **evidence(session, selected, stage, settings),
    )


def evidence(session: Any, selected: str, stage: str, settings: Any) -> dict[str, Any]:
    return dict(
        point=point(session, selected, stage),
        finding=finding(session, selected, settings),
        stacking=stacking(session, selected, stage),
        paint=paint(session, selected, stage),
        section=section(session, selected, settings.get("section", {})),
    )


def section(session: Any, selected: str, settings: Any) -> dict[str, Any]:
    from math import isfinite

    if not settings.get("enabled"):
        return {}
    if settings.get("target") != selected or settings.get("axis") not in (0, 1, 2):
        raise ValueError("Section target and axis must match the inspected tissue.")
    if not isfinite(settings["position"]):
        raise ValueError("Section position must be finite.")
    fields = ("enabled", "target", "axis", "position", "flip", "cut", "wholeScene")
    state = inspection.status(session, "section")
    report = state.get("report", {}) if state["state"] == "ready" else {}
    return dict(settings={key: settings[key] for key in fields}, report=report)


def stacking(session: Any, selected: str, stage: str) -> dict[str, Any]:
    value = inspection.status(session, "stacking")
    if stage != "intrinsic" or value["state"] != "ready" or value["target"] != selected:
        return {}
    asset = session.tissue_inspection.values["stacking"].asset
    return dict(options=asset["options"], report=value["report"])


def paint(session: Any, selected: str, stage: str) -> dict[str, Any]:
    value = inspection.status(session, "paint")
    if value["state"] != "ready" or value["target"] != selected:
        return {}
    asset = session.tissue_inspection.values["paint"].asset
    if asset["options"]["stage"] != stage:
        return {}
    return dict(options=asset["options"], report=value["report"], authored=False)


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
