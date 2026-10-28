"""Atomic reviewed graph adoption shared by desktop and headless clients."""

from typing import Any

from anthroforge.core.skeleton_update import require_review


def apply(session: Any, token: str, approved: list[str] | None = None) -> dict[str, Any]:
    candidate = session.skeleton_update.ready(token)
    require_review(candidate.findings, approved or [])
    for row in candidate.changes:
        session.editable(
            row.target if not row.added else candidate.document.entity(row.target).parent
        )
    updated = candidate.merge(session.document)
    install(session, candidate, updated)
    result = dict(
        identities=candidate.identities, affected=sorted({p.owner for p in candidate.prepared})
    )
    session.skeleton_update.cancel()
    return result


def install(session: Any, candidate: Any, updated: Any) -> None:
    from . import property_guards, skin_update_tasks

    property_guards.require_changes(session, session.document, updated)
    session.scheduler.invalidate_ports(set(candidate.prepared))
    for kind in session.resources.__dataclass_fields__:
        getattr(session.resources, kind).update(getattr(candidate.resources, kind))
    names = (*candidate.changed(), "skin", "_index", "_registry", "_mirrors", "_formulas")
    session.replace_document(
        accepted_outputs=candidate.prepared, **{key: getattr(updated, key) for key in names}
    )
    skin_update_tasks.pending(session)


def commands(session: Any) -> dict[str, Any]:
    service = session.skeleton_update
    return {
        "skeleton_update.inspect": service.inspect,
        "skeleton_update.prepare": service.prepare,
        "skeleton_update.status": service.status,
        "skeleton_update.cancel": service.cancel,
    }
