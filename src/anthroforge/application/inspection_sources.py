"""Adapters read completed candidate resources without publication or reevaluation."""

from typing import Any

from . import (
    curve_conversion,
    replacement_assessments,
    skin_fit_preview,
    surface_preview,
    tissue_preview,
)

SLOTS = dict(
    curve_conversion="conversion",
    surface="surface_preview",
    tissue_inflation="tissue_preview",
    mesh_replacement="mesh_replacement",
    tissue_retarget="tissue_retarget",
    skin_fit="skin_fit_preview",
)
STATUSES = dict(
    curve_conversion=curve_conversion.status,
    surface=surface_preview.status,
    tissue_inflation=tissue_preview.status,
    skin_fit=skin_fit_preview.status,
)


def status(session: Any, kind: str) -> Any:
    if kind in STATUSES:
        result = STATUSES[kind](session)
        value = getattr(session, SLOTS[kind])
        if stale_fitted(session, kind, value):
            return dict(result, state="stale")
        return result
    if kind in ("mesh_replacement", "tissue_retarget"):
        return replacement_assessments.status(session, kind)
    if kind in ("skeleton_update", "variant_review"):
        return getattr(session, kind).status()
    raise ValueError("Unknown inspection candidate kind: " + kind)


def stale_fitted(session: Any, kind: str, value: Any) -> bool:
    return kind == "skin_fit" and value.state == "ready" and not skin_fit_preview.displayed(session)


def ready(session: Any, kind: str, token: str) -> Any:
    result = status(session, kind)
    if not token or result.get("token") != token or result["state"] != "ready":
        raise ValueError("Capture requires the exact token of a completed, current candidate.")
    if kind in SLOTS:
        value = getattr(session, SLOTS[kind])
        if value.asset is None:
            raise ValueError("The candidate has no geometry to capture.")
        return value
    return getattr(session, kind).runtime.preparation


def available(session: Any, kind: str) -> Any:
    result = status(session, kind)
    return ready(session, kind, result["token"]) if result["state"] == "ready" else None
