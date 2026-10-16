"""Curve/handle/cage line preparation performed only when the authored revision changes."""

from dataclasses import replace

from anthroforge.application.control_frames import display_frame
from anthroforge.native import components, construction
from anthroforge.native.scene import entity_frame


def pairs(points, closed=False):
    return [
        value
        for i in range(len(points) if closed else len(points) - 1)
        for value in (points[i], points[(i + 1) % len(points)])
    ]


def curve_path(session, entity, curve):
    definition = replace(entity.primitive, samples=64, start=0, span=1)
    curve = replace(curve, start=None, span=None)
    samples = construction.sample_curve(session.engine, curve, definition)[:, :3]
    world = components.transformed(
        session.engine, samples, entity_frame(session.engine, entity)
    ).tolist()
    return pairs(world, curve.closed)


def handle_lines(session, entity, curve):
    handles = construction.resolved_curve(session.engine, curve)
    triples = handles[:, [3, 4, 5, 0, 1, 2, 6, 7, 8]].reshape((-1, 3))
    frame = construction.matrix(session.engine, entity_frame(session.engine, entity), curve.matrix)
    endpoints = components.transformed(session.engine, triples, frame).tolist()
    lines = [p for i in range(0, len(endpoints), 3) for p in pairs(endpoints[i : i + 3])]
    return lines


def cage_edges(resolution):
    u, v, w = resolution
    strides, dimensions = (1, u, u * v), (u, v, w)
    return [
        (i, i + stride)
        for i in range(u * v * w)
        for stride, count in zip(strides, dimensions, strict=True)
        if i // stride % count + 1 < count
    ]


def cage_lines(session, control):
    world = components.transformed(
        session.engine, control.points, display_frame(session, control)
    ).tolist()
    return [world[index] for edge in cage_edges(control.resolution) for index in edge]


def for_editor(editor):
    session, selected = editor.controller.session, editor.controller.selection
    control = next((c for c in session.document.controls if c.id == selected), None)
    if control:
        return (cage_lines(session, control) if control.kind == "LATTICE" else []), {}
    entity = next((e for e in session.document.entities if e.id == selected), None)
    if not editor.editing or not entity or not entity.primitive:
        return [], {}
    paths = {c.id: curve_path(session, entity, c) for c in entity.primitive.curves}
    lines = [point for path in paths.values() for point in path]
    lines += [p for c in entity.primitive.curves for p in handle_lines(session, entity, c)]
    return lines, paths if editor.category == "CURVE" else {}
