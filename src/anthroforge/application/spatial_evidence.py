"""Shared revision-qualified geometry witnesses for API, viewport and frozen exports."""

from typing import Any

from anthroforge.native import inspection

from . import inspection_surfaces


def witness(context: Any, surface: Any, other: Any, row: Any, bounds: Any) -> dict[str, Any]:
    return dict(surface_witness(context, surface, row, bounds), **other_witness(other, row[3]))


def surface_witness(context: Any, surface: Any, row: Any, bounds: Any) -> dict[str, Any]:
    return dict(
        asset=surface.asset,
        frame=surface.frame,
        triangle=row[2],
        bounds=bounds,
        target=surface.target,
        stage=surface.stage,
        accepted_revision=surface.revision,
        revision=context.document.revision,
    )


def other_witness(other: Any, triangle: int) -> dict[str, Any]:
    return dict(
        other=other.target,
        other_asset=other.asset,
        other_frame=other.frame,
        other_stage=other.stage,
        other_triangle=triangle,
    )


def current_surface(context: Any, witness: Any) -> Any:
    surface = inspection_surfaces.get(context, witness["target"], witness["stage"])
    if surface.asset != witness["asset"] or tuple(surface.frame) != tuple(witness["frame"]):
        raise ValueError("This finding describes an older surface. Check geometry again.")
    return surface


def capture(session: Any, row: Any) -> Any:
    return issue(session, row["id"]) if row else None


def lines(context: Any, witness: Any) -> list[Any]:
    surface = current_surface(context, witness)
    result = inspection.face_lines(surface.mesh(context), surface.frame, witness["triangle"])
    if witness["other_triangle"] >= 0:
        other = context.resources.meshes[witness["other_asset"]].mesh
        result += inspection.face_lines(other, witness["other_frame"], witness["other_triangle"])
    return result


def issue(session: Any, identity: str) -> dict[str, Any]:
    session.issues.listening.discover_changes()
    row = session.issues.presentation.get(identity)
    sample = row["evidence"].get("witness")
    if row["freshness"] != "current" or not sample:
        raise ValueError("A current spatial finding is required. Check geometry again.")
    current_surface(session, sample)
    return row
