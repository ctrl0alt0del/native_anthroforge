"""Interaction adapters invoke application commands; they do not edit document records."""

from PySide6.QtCore import QUrl

from anthroforge.application.session import Session
from anthroforge.core.entities import descendants
from anthroforge.core.results import geometry_asset
from anthroforge.native import scene

from . import object_interaction


def local_path(value):
    url = QUrl(value)
    return url.toLocalFile() if url.isLocalFile() else value


def run(controller, operation, arguments):
    try:
        result = controller.session.command(operation, **command_values(arguments))
        if operation in ("scp.empty", "scp.duplicate", "scp.wrap_root"):
            controller.selection = result
        controller.refresh()
        return result
    except Exception as error:
        controller.message = str(error)
        controller.notify()
        return None


def command_values(value):
    """JavaScript has one numeric type; restore exact integers at the Qt transport boundary."""
    if isinstance(value, dict):
        return {key: command_values(item) for key, item in value.items()}
    if isinstance(value, list):
        return [command_values(item) for item in value]
    if type(value) is float and value.is_integer():
        return int(value)
    return value


def start_transform(controller, mode):
    object_interaction.require_transform(controller)
    controller.drag_mode = mode
    if controller.authoring.active:
        from .authoring_actions import start_transform as start_components

        return start_components(controller.authoring, mode)
    if not controller.selection:
        return
    object_interaction.editable(controller)
    controller.session.begin()
    controller.drag_values = list(controller.selectedData["trs"])
    controller.drag_mode = mode


def drag_transform(controller, axis, amount):
    from .transform_delta import axis_values

    transform_delta(controller, axis_values(controller.drag_mode, axis, amount))


def transform_delta(controller, values):
    from .transform_delta import object_values

    if controller.authoring.active:
        from .authoring_actions import transform_delta as component_delta

        return component_delta(controller.authoring, values)
    if not controller.drag_values or controller.session.history.before is None:
        return
    result = object_values(controller.session.engine, controller.drag_values, values)
    run(controller, *object_interaction.transform_command(controller, result))


def end_transform(controller, cancel=False):
    if controller.session.history.before is not None:
        run(controller, "cancel" if cancel else "commit", {})
    controller.drag_values = []


def rebase_transform(controller, mode=""):
    if controller.session.history.before is None:
        return
    if controller.authoring.active:
        from .authoring_actions import capture_transform

        controller.authoring.drag_mode = mode or controller.authoring.drag_mode
        capture_transform(controller.authoring)
    else:
        controller.drag_values = list(controller.selectedData["trs"])


def selection_center(controller):
    selected = controller.authoring.transformData
    if not selected:
        selected = controller.selectedData
    if not selected:
        return []
    if selected["id"] == "components" or selected.get("is_control"):
        return selected["trs"][:3]
    item = controller.session.document.object(selected["id"])
    return frame_bounds(controller.session, item, selected["trs"][6:])[0]


def new_document(controller):
    old = controller.session
    controller.session = Session(profiler=controller.profiler)
    scene.configure(controller.session.engine)
    old.close()
    controller.selection, controller.last_revision = "", -1
    controller.refresh()


def frame(controller):
    selected = controller.selectedData
    if not selected:
        controller.frameRequested.emit([0.0, 0.0, 0.0, 4.0])
        return
    if selected.get("is_control"):
        controller.frameRequested.emit([*selected["trs"][:3], 1.0])
        return
    item = controller.session.document.object(selected["id"])
    center, radius = frame_bounds(controller.session, item, selected["trs"][6:])
    controller.frameRequested.emit([*center, max(0.02, radius * 2.5)])


def frame_bounds(session, item, scales):
    if item.id in session.document.registry.authored:
        return object_interaction.bounds(session, item)
    key = geometry_asset(item)
    if not key:
        return group_bounds(session, item)
    bounds = session.assets[key].mesh.bounds
    local = [(bounds[i] + bounds[i + 3]) / 2 + item.geometry_offset[i] for i in range(3)]
    radius = max(bounds[i + 3] - bounds[i] for i in range(3)) * max(map(abs, scales))
    return session.engine.world_point(item.matrix, local), radius


def group_bounds(session, item):
    members = descendants(session.document.entities, item.id) - set(session.workspace.hidden)
    entities = [e for e in session.document.entities if e.id in members and geometry_asset(e)]
    if not entities:
        return session.engine.world_point(item.matrix, item.geometry_offset), 1.0
    handles = [session.assets[geometry_asset(e)].mesh.handle for e in entities]
    matrices = [scene.entity_frame(session.engine, e) for e in entities]
    bounds = scene.bounds(session.engine, handles, matrices)
    center = [(bounds[i] + bounds[i + 3]) * 0.5 for i in range(3)]
    return center, max(bounds[i + 3] - bounds[i] for i in range(3))
