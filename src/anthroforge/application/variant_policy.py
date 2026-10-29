"""Shared editing capabilities keep pinned anatomy read-only in alternative contexts."""

from typing import Any

from dataclasses import replace


def allowed(session: Any, target: str) -> bool:
    return target not in session.editing_restrictions


def retain_scope(before: Any, after: Any) -> Any:
    if before.editing_scope is None or after.editing_scope is not before.editing_scope:
        return after
    from .skeleton_graph import identity
    from .variant_reconciliation import GROUPS

    added = set()
    for group in GROUPS:
        old, new = getattr(before, group), getattr(after, group)
        if old is not new:
            added |= {identity(v) for v in new} - {identity(v) for v in old}
    scope = replace(before.editing_scope, editable=before.editing_scope.editable | added)
    return replace(after, editing_scope=scope) if scope != after.editing_scope else after


def require(session: Any, target: str) -> None:
    if not allowed(session, target):
        raise ValueError(
            "This is a pinned external support; edit accepted anatomy or refresh supports."
        )


def included(session: Any, target: str) -> bool:
    from .workspace_policy import included as in_workspace

    return allowed(session, target) and in_workspace(session.document, session.workspace, target)


def command(session: Any, operation: str, arguments: Any) -> None:
    if not session._editing.key:
        return
    if operation.startswith("skin.") or operation in {
        "attachments.enable",
        "skeleton_update.apply",
    }:
        raise ValueError("Project-wide operations belong to accepted anatomy.")
    for name in ("entity", "target", "control", "curve", "surface"):
        key = arguments.get(name)
        if isinstance(key, str) and key in session.document.registry.records:
            require(session, key)
    if driver := arguments.get("driver"):
        require_driver(session, driver)


def require_driver(session: Any, driver: str) -> None:
    from .driving_operations import selected
    from .shortcut_ownership import targets

    for key in targets(session.document, selected(session, driver)):
        require(session, key)
