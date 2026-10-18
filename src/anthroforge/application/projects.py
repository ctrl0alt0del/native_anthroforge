"""Save policy and project adoption are shared across UI and automation."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .history import History
from .storage import FileLock, atomic_save, read_package

if TYPE_CHECKING:
    from .session import Session


def save(session: "Session", path: str, blocked_policy: str) -> dict[str, Any]:
    if session.history.before is not None:
        raise ValueError("Commit or cancel the active edit before saving.")
    if blocked_policy not in ("wait", "checkpoint", "pending"):
        raise ValueError("Explicit blocked_policy must be wait, checkpoint, or pending.")
    session.scheduler.tick()
    if session.scheduler.blocked and blocked_policy == "pending":
        return {
            "status": "pending",
            "jobs": [j.id for j in session.scheduler.active_jobs if j.writes],
        }
    if blocked_policy == "wait":
        session.scheduler.wait(writes_only=True)
    document = session.scheduler.checkpoint if session.scheduler.blocked else session.document
    return save_snapshot(session, Path(path).resolve(), document)


def save_snapshot(session: "Session", target: Path, document: Any) -> dict[str, Any]:
    lock = lock_target(session, target)
    try:
        atomic_save(target, document, session.resources.snapshot())
    except Exception:
        if lock is not session.file_lock:
            lock.close()
        raise
    return finish_save(session, target, lock, document.revision)


def lock_target(session: "Session", target: Path) -> FileLock:
    if session.file_lock and session.file_lock.path == target:
        return session.file_lock  # type: ignore[no-any-return]
    return FileLock(target)


def finish_save(session: "Session", target: Path, lock: FileLock, revision: int) -> dict[str, Any]:
    if session.file_lock and session.file_lock is not lock:
        session.file_lock.close()
    session.path, session.file_lock = target, lock
    session.saved_revision = revision
    return {"status": "saved", "path": str(target), "revision": revision}


def open_project(session: "Session", path: str) -> dict[str, Any]:
    target = Path(path).resolve(strict=True)
    lock = lock_target(session, target)
    try:
        document, assets = read_package(target, session.engine)
    except Exception:
        if lock is not session.file_lock:
            lock.close()
        raise
    adopt(session, document, assets)
    finish_save(session, target, lock, document.revision)
    synchronize_loaded(session)
    return session.describe()


def adopt(session: "Session", document: Any, assets: Any) -> None:
    session.issues.close()
    session.scheduler.close()
    session.document, session.resources = document, assets
    session.history = History(document)
    session.serial = document.revision
    session.initialize_scheduler()
    session.active_workspace = 0


def synchronize_loaded(session: "Session") -> None:
    from .evaluation import request

    targets = {item.id for item in session.document.entities if item.parent}
    captures = {
        item.id
        for item in session.document.entities
        if item.parent and (not item.attachment.binding or item.status == "edited")
    }
    if targets and session.document.attachments_enabled:
        request(session, targets, captures)
