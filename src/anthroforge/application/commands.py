"""One explicit operation catalogue; no active Blender context or Python eval."""

from typing import TYPE_CHECKING, Any

from . import evaluation, importing, operations, presentation, projects

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
        "begin": session.begin,
        "commit": session.commit,
        "cancel": session.cancel,
        "undo": lambda: session.navigate(-1),
        "redo": lambda: session.navigate(1),
        "inspect": session.describe,
        "wait": session.scheduler.wait,
        "tick": session.scheduler.tick,
        "job.cancel": session.scheduler.cancel_job,
        "job.retry": session.scheduler.retry,
        "evaluate": lambda: evaluate(session),
    }


def file_commands(session: "Session") -> dict[str, Any]:
    return {
        "save": lambda **a: projects.save(session, **a),
        "open": lambda **a: projects.open_project(session, **a),
        "workspace.create": lambda **a: presentation.create_workspace(session, **a),
        "workspace.select": lambda **a: presentation.select_workspace(session, **a),
        "workspace.update": lambda **a: presentation.update_workspace(session, **a),
    }


def evaluate(session: "Session") -> str:
    targets = {item.id for item in session.document.entities}
    captures = {
        item.id
        for item in session.document.entities
        if item.status == "edited" or not item.attachment.binding
    }
    return evaluation.request(session, targets, captures)
