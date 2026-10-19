"""Tissue parameter controls share component selection without exposing derived vertex edits."""

from anthroforge.application.object_frames import Frames
from anthroforge.application.tissue_part_operations import control_value, selected
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import components


def records(editor, item):
    from . import tissue_field_editor

    if editor.category == "TISSUE_FIELD":
        return tissue_field_editor.records(editor, item)
    return controls(editor, item)


def controls(editor, item):
    if not isinstance(item, TissueVCP) or editor.category != "TISSUE_CONTROL":
        return []
    session = editor.controller.session
    part, side = editor.tissue_context
    inflation = getattr(selected(item, part), side).inflation
    if inflation.mode != "CTRL_POINT" or (side == "b" and not item.both_sides):
        return []
    local = inflation.control or control_value(session, item, part)
    frame = Frames(session.engine, session.document).world(item.id)
    world = components.transformed(session.engine, [local], frame)[0].tolist()
    reference = dict(
        owner=item.id, piece=part, side=side, part="tissue_control", index=int(side == "b")
    )
    return [(reference, world, list(local))]


def projected(item):
    return dict(id=item.id, name=item.name, kind="TISSUE", source=item.source)


def edit(editor, part, side):
    editor.controller.cancelViewportTools()
    editor.tissue_context = (part, side)
    editor.category, editor.editing, editor.selection = "TISSUE_CONTROL", True, []
    editor.refresh()
    if editor.componentRows:
        editor.selectComponent(editor.componentRows[0]["key"], False)
