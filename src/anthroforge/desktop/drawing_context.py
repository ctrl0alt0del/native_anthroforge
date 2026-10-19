"""Capture displayed geometry once per stroke, never authored or staged replacements."""

from dataclasses import asdict
from math import isfinite, radians

from anthroforge.core.drawing import FitSettings, ProjectionSettings
from anthroforge.native import strokes


def capture(tool, normal):
    controller, options = tool.controller, tool.options
    handles, frames = surface_inputs(tool)
    plane = depth_plane(tool, normal)
    settings = ProjectionSettings(
        **{key: options[key] for key in ("depth", "first_plane", "offset", "relative")}
    )
    return strokes.Stroke(controller.session.engine, handles, frames, plane, settings.packed())


def surface_inputs(tool):
    controller, options = tool.controller, tool.options
    selected = set(controller.selectedObjects)
    indices = [
        i
        for i, key in enumerate(controller.snap_ids)
        if options["depth"] != "SURFACE" or not options["selected_only"] or key in selected
    ]
    handles, frames = controller.snap_handles[indices], controller.snap_matrices[indices]
    tool.leases = tuple(controller.render_model.leases[int(key)] for key in handles)
    return handles, frames


def depth_plane(tool, normal):
    controller = tool.controller
    if tool.options["depth"] != "IMAGE":
        return [*controller.session.workspace.cursor, *normal]
    selected = tool.options["image"] or controller.selection
    rows = controller.image_model.active_rows()
    row = next((r for r in rows if r["id"] == selected), None)
    if row is None:
        raise ValueError("Select a displayed reference image for image-plane drawing.")
    return strokes.plane(controller.session.engine, row["matrix"])


def point_records(samples):
    return [dict(position=row[:3], radius=row[3]) for row in samples]


def fit_settings(options):
    return asdict(
        FitSettings(
            method=options["method"],
            error=options["error"],
            closed=options["closed"],
            corner_angle=radians(options["corner_angle"]),
        )
    )


def substeps(options, mode):
    return mode == "DRAW" and options["depth"] == "SURFACE" and options["method"] != "POLYLINE"


def finish_settings(tool):
    settings = fit_settings(tool.options)
    measured = tool.stroke.settings(tool.options["error_pixels"])
    if tool.options["auto_close"]:
        settings["closed"] = settings["closed"] or measured["closed"]
    if tool.options["screen_error"] and measured["error"] > 0:
        settings["error"] = measured["error"]
    return settings


def validate_settings(options):
    ProjectionSettings(
        **{key: options[key] for key in ("depth", "first_plane", "offset", "relative")}
    )
    fit_settings(options)
    if not isfinite(options["radius"]) or options["radius"] < 0:
        raise ValueError("Drawing radius must be finite and nonnegative.")
    if not isfinite(options["error_pixels"]) or options["error_pixels"] <= 0:
        raise ValueError("Drawing pixel tolerance must be positive and finite.")
