"""Interaction adapters invoke application commands; they do not edit document records."""

from PySide6.QtCore import QUrl

from anthroforge.application.session import Session
from anthroforge.core.entities import descendants
from anthroforge.core.results import geometry_asset
from anthroforge.native import scene


def local_path(value):
    url = QUrl(value)
    return url.toLocalFile() if url.isLocalFile() else value


def run(controller, operation, arguments):
    try:
        result = controller.session.command(operation, **arguments)
        if operation in ("scp.empty", "scp.duplicate", "scp.wrap_root"):
            controller.selection = result
        controller.refresh()
        return result
    except Exception as error:
        controller.message = str(error)
        controller.notify()
        return None


def start_transform(controller, mode):
    if controller.authoring.active:
        from .authoring_actions import start_transform as start_components

        return start_components(controller.authoring, mode)
    if not controller.selection:
        return
    controller.session.editable(controller.selection)
    controller.session.begin()
    controller.drag_values = list(controller.selectedData["trs"])
    controller.drag_mode = mode


def drag_transform(controller, axis, amount):
    if controller.authoring.active:
        from .authoring_actions import drag_transform as drag_components

        return drag_components(controller.authoring, axis, amount)
    if not controller.drag_values:
        return
    values = list(controller.drag_values)
    mode = controller.drag_mode
    index = axis + {"Move": 0, "Rotate": 3, "Scale": 6}[mode]
    if mode == "Scale":
        values[index] *= max(0.01, 1.0 + amount)
    else:
        values[index] += amount * (60.0 if mode == "Rotate" else 1.0)
    run(controller, "scp.transform", {"entity": controller.selection, "values": values})


def end_transform(controller, cancel=False):
    if controller.session.history.before is not None:
        run(controller, "cancel" if cancel else "commit", {})
    controller.drag_values = []


def new_document(controller):
    old = controller.session
    controller.session = Session()
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
    item = controller.session.document.entity(selected["id"])
    center, radius = frame_bounds(controller.session, item, selected["trs"][6:])
    controller.frameRequested.emit([*center, max(0.02, radius * 2.5)])


def frame_bounds(session, item, scales):
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
