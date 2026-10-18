"""Cached native component indices and deliberate whole-curve selection."""

import numpy as np

from anthroforge.native.components import PickIndex

from . import authoring_lines, authoring_state, presentation


def prepare(editor):
    engine = editor.controller.session.engine
    editor.rows = authoring_state.components_for(editor)
    editor._lines, editor._curve_lines = authoring_lines.for_editor(editor)
    editor._points = np.asarray([r[1] for r in editor.rows], dtype=np.float64).reshape((-1, 3))
    prepare_indices(editor, engine)
    editor._curve_members = curve_members(editor.rows)


def prepare_indices(editor, engine):
    indices = [
        i for i, (r, _, _) in enumerate(editor.rows) if presentation.component(editor, r, True)
    ]
    editor._point_index = PickIndex(engine, editor._points[indices], labels=indices)
    paths = (
        list(editor._curve_lines.values()) if presentation.allows(editor, "curves", True) else []
    )
    segments = [point for path in paths for point in path]
    labels = [index for index, path in enumerate(paths) for _ in range(len(path) // 2)]
    editor._curve_index = PickIndex(engine, segments, segments=True, labels=labels)
    editor._curve_ids = list(editor._curve_lines)
    retain_hover(editor, indices, paths)


def retain_hover(editor, indices, paths):
    if editor.hover_index not in indices:
        editor.hover_index = -1
    if not paths:
        editor.hover_curve = ""


def curve_members(rows):
    result = {}
    for reference, _, _ in rows:
        if reference.get("curve") and reference["part"] == "position":
            result.setdefault(reference["curve"], []).append(
                authoring_state.component_key(reference)
            )
    return result


def pick(editor, origin, direction, radius, depth, select, extend):
    index = editor._point_index.pick(origin, direction, radius, depth)
    curve = editor._curve_index.pick(origin, direction, radius * 0.6, depth) if index < 0 else -1
    curve_id = editor._curve_ids[curve] if curve >= 0 else ""
    editor.update_hover(index, curve_id)
    if select:
        if curve_id:
            select_curve(editor, curve_id, extend)
        else:
            editor.selectComponent(
                authoring_state.component_key(editor.rows[index][0]) if index >= 0 else "", extend
            )
    return index >= 0 or curve >= 0


def select_curve(editor, curve, extend):
    members = editor._curve_members.get(curve, [])
    selected = set(editor.selection) if extend else set()
    editor.selection = sorted(
        selected - set(members) if set(members) <= selected else selected | set(members)
    )
    editor.notify()
