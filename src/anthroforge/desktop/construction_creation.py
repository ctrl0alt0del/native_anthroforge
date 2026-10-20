"""Creation from ordered selected sources uses shared consumer operations."""

from anthroforge.core.construction import Curve
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.object_registry import validate_sources
from anthroforge.core.surfaces import Surface


def selected_curves(controller):
    records = controller.session.document.registry.construction
    return [key for key in controller.selectedObjects if isinstance(records.get(key), Curve)]


def surface(controller, kind):
    return controller.surface_creation.request(selected_curves(controller), kind)


def surface_action(controller):
    curves = selected_curves(controller)
    if not curves:
        return dict(enabled=False, hint="Select one closed curve or two or more curves")
    kind = "PATCH" if len(curves) == 1 else "LOFT"
    hint = "Patch selected closed curve" if kind == "PATCH" else "Create Surface · Detect branches"
    try:
        item = Surface(kind=kind, curves=tuple(CurveUse(key) for key in curves))
        validate_sources(item, controller.session.document.registry.records)
        return dict(enabled=True, hint=hint)
    except ValueError as error:
        return dict(enabled=False, hint=str(error))


def create(editor, kind, shape):
    controller, args = editor.controller, editor.create_arguments(kind, shape)
    curves = selected_curves(controller)
    operation = "primitive.from_curves" if curves else "primitive.create"
    if curves:
        args["curves"] = curves
    entity = controller.run(operation, args)
    if entity:
        controller.select(entity)
        editor.setEditing(True)
