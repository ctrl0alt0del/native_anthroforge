"""Expose wrappers without changing their underlying properties or activating policies."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.entities import descendants
from anthroforge.core.numeric_properties import PropertyRef, decode_reference
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


def set_value(
    session: Any,
    reference: dict[str, Any],
    value: Any,
    uniform: bool = False,
    component: int | None = None,
) -> None:
    from .property_operations import set_value as property_set

    selected = editable_wrapper(session, reference)
    session.shortcut_edits.begin(selected)
    target = asdict(component_reference(selected.reference, component))
    property_set(session, target, value, uniform)


def component_reference(reference: PropertyRef, component: int | None) -> PropertyRef:
    return replace(reference, component=component) if component is not None else reference


def editable_wrapper(session: Any, reference: dict[str, Any]) -> Shortcut:
    selected = wrapper(session, reference)
    validate_policy(session.document, selected)
    return selected


def validate_policy(document: Any, shortcut: Any) -> None:
    policy = shortcut.policy
    owner = shortcut_ownership.attachment_scope(document, shortcut)
    if policy.scope and (
        owner not in document.index.entities
        or owner not in shortcut_ownership.owners(document, shortcut)
    ):
        raise ValueError("Choose an attachment scope among the shortcut's controlled SCPs.")
    if not owner and (policy.backsolve or policy.descendants):
        raise ValueError(
            "Attachment policies require one inferred owning SCP or an explicit scope."
        )
    allowed = descendants(document.entities, owner) - {owner} if owner else set()
    if any(v.target not in allowed for v in policy.descendants):
        raise ValueError("Attachment overrides apply only to descendants of the attachment scope.")


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
    values = ordered(session.document)
    result = []
    for value in values:
        owners = shortcut_ownership.owners(session.document, value)
        if value.exposed and (not selected or owners == {selected}):
            if search.casefold() in search_label(session.document, value).casefold():
                result.append(dict(asdict(value), id=value.id, owners=sorted(owners)))
    return result


def search_label(document: Any, value: Any) -> str:
    if value.label or not isinstance(value, Shortcut):
        return str(value.label)
    try:
        return str(property_catalog.resolve(document, value.reference).label)
    except ValueError:
        return "Missing property"


def reorder(session: Any, identities: list[str]) -> None:
    values = {v.id: v for v in ordered(session.document)}
    if len(identities) != len(values) or set(identities) != values.keys():
        raise ValueError("Reordering must include each existing shortcut once.")
    session.replace_document(shortcut_order=tuple(identities))


def ordered(document: Any) -> tuple[Any, ...]:
    values = {v.id: v for v in (*document.shortcuts, *document.driving_shortcuts)}
    order = [key for key in document.shortcut_order if key in values]
    order.extend(key for key in values if key not in order)
    return tuple(values[key] for key in order)
