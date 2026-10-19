"""Selected-object interaction routes to shared policies and application commands."""

from itertools import product

from anthroforge.application import curve_sources, object_operations
from anthroforge.application.transform_policy import require_object_transform
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface
from anthroforge.native import components


def editable(controller):
    session, selected = controller.session, controller.selection
    if selected in session.document.registry.construction:
        return object_operations.editable(session, selected)
    return session.editable(selected)


def require_transform(controller):
    selected = controller.authoring.transformData
    if not selected or selected.get("readonly"):
        raise ValueError("Select editable objects or curve components to transform.")
    if selected["id"] != "components":
        require_object_transform(controller.session.document.object(selected["id"]))


def transform_command(controller, values):
    if controller.selection in controller.session.document.registry.construction:
        return "object.transform", dict(target=controller.selection, values=values, world=True)
    return "scp.transform", dict(entity=controller.selection, values=values)


def bounds(session, item):
    frame = curve_sources.world(session.engine, session.document, item.id)
    local = local_bounds(session, item)
    if local is None:
        return session.engine.world_point(frame, (0, 0, 0)), 1.0
    corners = list(product(*[(local[i], local[i + 3]) for i in range(3)]))
    world = session.engine.bounds(components.transformed(session.engine, corners, frame).ravel())
    return [(world[i] + world[i + 3]) * 0.5 for i in range(3)], max(
        world[i + 3] - world[i] for i in range(3)
    )


def local_bounds(session, item):
    if isinstance(item, ReferenceImage):
        return (-item.width / 2, -item.height / 2, 0, item.width / 2, item.height / 2, 0)
    if isinstance(item, Surface):
        asset = session.assets.get(item.result.asset)
        return asset.mesh.bounds if asset else None
    resource = session.resources.paths.get(item.result.asset)
    return resource.path.bounds if resource else None
