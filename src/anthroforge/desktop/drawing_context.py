"""Capture displayed geometry once per stroke, never authored or staged replacements."""

from anthroforge.native import strokes


def capture(tool, normal):
    controller, options = tool.controller, tool.options
    handles, frames = surface_inputs(tool)
    plane = depth_plane(tool, normal)
    settings = [
        options["depth"] == "SURFACE",
        options["first_plane"],
        options["offset"],
        options["relative"],
    ]
    return strokes.Stroke(controller.session.engine, handles, frames, plane, settings)


def surface_inputs(tool):
    controller, options = tool.controller, tool.options
    selected = set(controller.selectedObjects)
    indices = [
        i
        for i, key in enumerate(controller.snap_ids)
        if not options["selected_only"] or key in selected
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
