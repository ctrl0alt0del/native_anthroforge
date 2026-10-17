"""One explicit operation catalogue; no active Blender context or Python eval."""

from typing import TYPE_CHECKING, Any

from . import construction_tasks, evaluation, importing, operations, presentation, projects
from . import control_operations as controls
from . import deformer_operations as deformers
from . import primitive_operations as primitives

if TYPE_CHECKING:
    from .session import Session

EDITS = {
    "scp.empty": operations.empty,
    "scp.rename": operations.rename,
    "scp.color": operations.color,
    "scp.delete": operations.delete,
    "scp.duplicate": operations.duplicate,
    "scp.reparent": operations.reparent,
    "scp.wrap_root": operations.wrap_root,
    "scp.transform": operations.transform,
    "scp.attachment": operations.attachment,
    "scp.recapture": operations.recapture,
    "scp.origin": operations.move_origin,
    "attachments.enable": operations.toggle_attachments,
    "update_mode": operations.update_mode,
    "import": importing.import_mesh,
    "primitive.create": primitives.create,
    "primitive.update": primitives.update,
    "curve.update": primitives.curve_update,
    "curve.add": primitives.curve_add,
    "curve.remove": primitives.curve_remove,
    "curve.order": primitives.curve_order,
    "curve.split": primitives.curve_split,
    "point.update": primitives.point_update,
    "point.insert": primitives.point_insert,
    "point.remove": primitives.point_remove,
    "body.update": primitives.piece_update,
    "thickness.update": primitives.thickness,
    "control.create": controls.create,
    "control.transform": controls.transform,
    "control.follow": controls.follow,
    "control.update": controls.update,
    "control.attach": controls.attach,
    "control.delete": controls.delete,
    "lattice.point": controls.lattice_point,
    "lattice.resize": controls.lattice_resize,
    "deformer.add": deformers.add,
    "deformer.update": deformers.update,
    "deformer.remove": deformers.remove,
    "deformer.order": deformers.order,
    "hook.reset": deformers.reset,
    "hook.recenter": deformers.recenter,
}


def execute(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    if operation in EDITS:
        return edit(session, operation, arguments)
    direct = direct_commands(session)
    if operation not in direct:
        raise ValueError(f"Unknown operation: {operation}")
    return direct[operation](**arguments)


def edit(session: "Session", operation: str, arguments: dict[str, Any]) -> Any:
    implicit = session.history.before is None
    if implicit:
        session.begin()
    try:
        result = EDITS[operation](session, **arguments)  # type: ignore[operator]
        if implicit:
            session.commit()
        return result
    except Exception:
        if implicit and session.history.before is not None:
            session.cancel()
        raise


def direct_commands(session: "Session") -> dict[str, Any]:
    return {
        **file_commands(session),
        **query_commands(session),
        "begin": session.begin,
        "commit": session.commit,
        "cancel": session.cancel,
        "undo": lambda: session.navigate(-1),
        "redo": lambda: session.navigate(1),
        "inspect": session.describe,
        "wait": session.wait,
        "tick": session.scheduler.tick,
        "evaluate": lambda **a: evaluate(session, **a),
    }


def query_commands(session: "Session") -> dict[str, Any]:
    return {
        "job.cancel": session.scheduler.cancel_job,
        "job.retry": session.scheduler.retry,
        "primitive.inspect": lambda **a: primitives.inspect(session, **a),
        "control.affected": lambda **a: controls.affected(session, **a),
        "deformer.members": lambda **a: deformers.members(session, **a),
    }


def file_commands(session: "Session") -> dict[str, Any]:
    return {
        "save": lambda **a: projects.save(session, **a),
        "open": lambda **a: projects.open_project(session, **a),
        "workspace.create": lambda **a: presentation.create_workspace(session, **a),
        "workspace.select": lambda **a: presentation.select_workspace(session, **a),
        "workspace.update": lambda **a: presentation.update_workspace(session, **a),
    }


def evaluate(session: "Session", entities: list[str] | None = None) -> str:
    targets = (
        set(entities) if entities is not None else {item.id for item in session.document.entities}
    )
    construction_tasks.evaluate(session, entities)
    captures = {
        item.id
        for item in session.document.entities
        if item.status == "edited" or not item.attachment.binding
    }
    return evaluation.request(session, targets, captures)
