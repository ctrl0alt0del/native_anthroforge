"""Creation from ordered selected sources uses shared consumer operations."""

from anthroforge.core.construction import Curve


def selected_curves(controller):
    records = controller.session.document.registry.construction
    return [key for key in controller.selectedObjects if isinstance(records.get(key), Curve)]


def surface(controller, kind):
    from .image_tools import context_owner

    curves = selected_curves(controller)
    closed = any(controller.session.document.object(key).closed for key in curves)
    return controller.run(
        "surface.preview" if kind == "LOFT" and closed else "surface.create",
        dict(curves=curves, kind=kind, owner=context_owner(controller)),
    )


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
