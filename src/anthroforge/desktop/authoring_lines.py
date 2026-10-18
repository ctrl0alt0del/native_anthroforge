"""Curve/handle/cage line preparation performed only when the authored revision changes."""


from anthroforge.application.control_frames import display_frame
from anthroforge.native import construction, control_geometry

from . import curve_context


def curve_path(session, entity, curve):
    key = session.document.object(curve.id).result.asset
    if key not in session.resources.paths:
        return []
    samples = session.resources.paths[key].path.array()[:, :3]
    return control_geometry.polylines(
        session.engine, samples, curve_context.frame(session, entity, curve), curve.closed
    ).tolist()


def handle_lines(session, entity, curve):
    if curve.engine != "BEZIER":
        return []
    handles = construction.resolved_curve(session.engine, curve)
    triples = handles[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    frame = curve_context.frame(session, entity, curve)
    return control_geometry.polylines(session.engine, triples, frame, group=3).tolist()


def cage_lines(session, control):
    return control_geometry.cage_lines(
        session.engine, control.points, control.resolution, display_frame(session, control)
    ).tolist()


def for_editor(editor):
    session, selected = editor.controller.session, editor.controller.selection
    control = next((c for c in session.document.controls if c.id == selected), None)
    if control:
        return (cage_lines(session, control) if control.kind == "LATTICE" else []), {}
    entity, curves = curve_context.owner(editor), curve_context.curves(editor)
    if not editor.editing or not curves:
        return [], {}
    paths = {c.id: curve_path(session, entity, c) for c in curves}
    lines = [point for path in paths.values() for point in path]
    lines += [p for c in curves for p in handle_lines(session, entity, c)]
    return lines, paths if editor.category == "CURVE" else {}
