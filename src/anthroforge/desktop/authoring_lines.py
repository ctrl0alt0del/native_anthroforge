"""Curve/handle/cage line preparation performed only when the authored revision changes."""

from dataclasses import replace

from anthroforge.application.control_frames import display_frame
from anthroforge.application.curve_sources import for_editing
from anthroforge.native import construction, control_geometry
from anthroforge.native.scene import entity_frame


def curve_path(session, entity, curve):
    definition = replace(entity.primitive, samples=64, start=0, span=1)
    curve = replace(curve, start=None, span=None)
    samples = construction.sample_curve(session.engine, curve, definition)[:, :3]
    return control_geometry.polylines(
        session.engine, samples, entity_frame(session.engine, entity), curve.closed
    ).tolist()


def handle_lines(session, entity, curve):
    handles = construction.resolved_curve(session.engine, curve)
    triples = handles[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    frame = construction.matrix(session.engine, entity_frame(session.engine, entity), curve.matrix)
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
    entity = next((e for e in session.document.entities if e.id == selected), None)
    entity = for_editing(session, entity)
    if not editor.editing or not entity or not entity.primitive:
        return [], {}
    paths = {c.id: curve_path(session, entity, c) for c in entity.primitive.curves}
    lines = [point for path in paths.values() for point in path]
    lines += [p for c in entity.primitive.curves for p in handle_lines(session, entity, c)]
    return lines, paths if editor.category == "CURVE" else {}
