"""One editor context for standalone curves and curves presented through a consumer."""

from dataclasses import replace

from anthroforge.application import curve_sources
from anthroforge.core.construction import Curve
from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.native import construction
from anthroforge.native.scene import entity_frame


def owner(editor):
    session = editor.controller.session
    item = session.document.registry.records.get(editor.controller.selection)
    return curve_sources.for_editing(session, item) if isinstance(item, SCP) else item


def curves(editor):
    item = owner(editor)
    if isinstance(item, Curve):
        return (replace(item, matrix=IDENTITY),)
    definition = getattr(item, "primitive", None)
    return definition.curves if definition else ()


def frame(session, item, curve=None):
    if isinstance(item, Curve):
        return curve_sources.world(session.engine, session.document, item.id)
    matrix = entity_frame(session.engine, item)
    return construction.matrix(session.engine, matrix, curve.matrix) if curve else matrix


def command(editor, operation, arguments):
    selected = editor.controller.selection
    item = editor.controller.session.document.registry.construction.get(selected)
    if not isinstance(item, Curve):
        return editor.controller.run(operation, arguments)
    return editor.controller.run(*standalone(operation, arguments))


def standalone(operation, arguments):
    names = {
        "point.update": "curve.point.update",
        "point.insert": "curve.point.insert",
        "point.remove": "curve.point.remove",
        "curve.split": "curve.subdivide",
        "curve.update": "curve.edit",
    }
    if operation not in names:
        raise ValueError("This operation requires a primitive consumer.")
    return names[operation], {key: value for key, value in arguments.items() if key != "entity"}
