"""Atomic reviewed graph adoption shared by desktop and headless clients."""

from typing import Any

from anthroforge.core.skeleton_update import require_review

PUBLICATION_FIELDS = (
    "skin",
    "shortcut_order",
    "editing_scope",
    "_index",
    "_registry",
    "_mirrors",
    "_formulas",
)


def apply(session: Any, token: str, approved: list[str] | None = None) -> dict[str, Any]:
    candidate = session.skeleton_update.ready(token)
    require_review(candidate.findings, approved or [])
    for row in candidate.changes:
        session.editable(
            row.target if not row.added else candidate.document.entity(row.target).parent
        )
    updated = candidate.merge(session.document)
    adopt_reviewed(session, candidate, updated)
    result = dict(
        identities=candidate.identities, affected=sorted({p.owner for p in candidate.prepared})
    )
    session.skeleton_update.cancel()
    return result


def adopt_reviewed(session: Any, candidate: Any, updated: Any) -> None:
    from .property_guards import publication

    formulas = {p.owner for p in candidate.prepared if p.output == "formula"}
    formulas.update(candidate.retained_formulas)
    disabled = frozenset(f.key[8:] for f in candidate.findings if f.key.startswith("disable:"))
    with publication(session, formulas, disabled):
        install(session, candidate, updated)


def install(session: Any, candidate: Any, updated: Any) -> None:
    from . import property_guards, skin_update_tasks

    property_guards.require_changes(session, session.document, updated)
    session.scheduler.invalidate_ports(set(candidate.prepared))
    for kind in session.resources.__dataclass_fields__:
        getattr(session.resources, kind).update(getattr(candidate.publication_resources, kind))
    names = (*candidate.changed(), *PUBLICATION_FIELDS)
    session.replace_document(
        accepted_outputs=candidate.prepared, **{key: getattr(updated, key) for key in names}
    )
    skin_update_tasks.pending(session)
