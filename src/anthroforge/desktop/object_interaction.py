"""Selected-object interaction routes to shared policies and application commands."""

from itertools import product

from anthroforge.application import curve_sources, object_operations
from anthroforge.native import components


def editable(controller):
    session, selected = controller.session, controller.selection
    if selected in session.document.registry.construction:
        return object_operations.editable(session, selected)
    return session.editable(selected)


def transform_command(controller, values):
    if controller.selection in controller.session.document.registry.construction:
        return "object.transform", dict(target=controller.selection, values=values, world=True)
    return "scp.transform", dict(entity=controller.selection, values=values)


def bounds(session, item):
    frame = curve_sources.world(session.engine, session.document, item.id)
    resource = session.resources.paths.get(item.result.asset)
    if resource is None:
        return session.engine.world_point(frame, (0, 0, 0)), 1.0
    local = resource.path.bounds
    corners = list(product(*[(local[i], local[i + 3]) for i in range(3)]))
    world = session.engine.bounds(components.transformed(session.engine, corners, frame).ravel())
    return [(world[i] + world[i + 3]) * 0.5 for i in range(3)], max(
        world[i + 3] - world[i] for i in range(3)
    )
