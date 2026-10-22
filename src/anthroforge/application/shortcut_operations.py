"""Expose wrappers without changing their underlying properties or activating policies."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.entities import descendants
from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.shortcuts import Shortcut

from . import property_catalog, shortcut_codec, shortcut_ownership


def wrapper(session: Any, reference: dict[str, Any]) -> Shortcut:
    ref = decode_reference(reference)
    property_catalog.resolve(session.document, ref)
    return next((s for s in session.document.shortcuts if s.reference == ref), Shortcut(ref))


def expose(session: Any, reference: dict[str, Any], label: str = "", exposed: bool = True) -> str:
    value = replace(wrapper(session, reference), exposed=exposed, label=label)
    install(session, value)
    return value.id


def configure(session: Any, reference: dict[str, Any], policy: dict[str, Any]) -> None:
    value = replace(wrapper(session, reference), policy=shortcut_codec.policy(policy))
    validate_policy(session.document, value)
    install(session, value)


def validate_policy(document: Any, shortcut: Any) -> None:
    policy = shortcut.policy
    owner = shortcut_ownership.scp_owner(document, shortcut)
    if not owner and (policy.backsolve or policy.descendants):
        raise ValueError("Attachment policies require one inferred owning SCP.")
    allowed = descendants(document.entities, owner) - {owner} if owner else set()
    if any(v.target not in allowed for v in policy.descendants):
        raise ValueError("Attachment overrides apply only to descendants of the owning SCP.")


def install(session: Any, shortcut: Shortcut) -> None:
    from .property_writes import editable

    editable(session, shortcut.reference.target)
    current = session.document.shortcuts
    if any(v.id == shortcut.id for v in current):
        current = tuple(shortcut if v.id == shortcut.id else v for v in current)
    else:
        current = (*current, shortcut)
    session.replace_document(shortcuts=current)


def inspect(session: Any, reference: dict[str, Any]) -> dict[str, Any]:
    value = wrapper(session, reference)
    return dict(
        asdict(value),
        id=value.id,
        owners=sorted(shortcut_ownership.owners(session.document, value)),
        scp_owner=shortcut_ownership.scp_owner(session.document, value),
    )


def listing(session: Any, selected: str = "", search: str = "") -> list[dict[str, Any]]:
    values = (*session.document.shortcuts, *session.document.driving_shortcuts)
    result = []
    for value in values:
        owners = shortcut_ownership.owners(session.document, value)
        if value.exposed and (not selected or owners == {selected}):
            if search.casefold() in value.label.casefold():
                result.append(dict(asdict(value), id=value.id, owners=sorted(owners)))
    return result


def reorder(session: Any, identities: list[str]) -> None:
    values = {v.id: v for v in session.document.shortcuts}
    if len(identities) != len(values) or set(identities) != values.keys():
        raise ValueError("Reordering must include each existing property wrapper once.")
    session.replace_document(shortcuts=tuple(values[key] for key in identities))
