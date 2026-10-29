"""Project metadata has one transaction owner, independent from active geometry contexts."""

from dataclasses import replace
from typing import Any

from anthroforge.core.reconstruction import next_record

from . import variant_operations


def state(session: Any) -> Any:
    return variant_operations.state(session)


def install(session: Any, **changes: Any) -> None:
    variant_operations.require_idle(session)
    variant_operations.install(session, replace(state(session), **changes))


def upsert(session: Any, group: str, row: Any) -> Any:
    rows = getattr(state(session), group)
    selected = tuple(row if old.id == row.id else old for old in rows)
    if not any(old.id == row.id for old in rows):
        selected += (row,)
    install(session, **{group: selected})
    return row.id


def selected(session: Any, group: str, key: str) -> Any:
    return next_record(getattr(state(session), group), key, group)


def scene(session: Any, variant: str = "") -> Any:
    if not variant:
        return session.contexts.scene("")
    value = state(session)
    return value.snapshot(value.variant(variant).current)


def subject(session: Any, key: str, variant: str = "") -> Any:
    document = scene(session, variant)
    if key in document.mirrors.instances:
        raise ValueError("Mirrors inherit their source's catalogue and reviews; select the source.")
    if key not in document.registry.anatomy:
        raise ValueError("Choose an SCP or tissue in this context.")
    return document.object(key)


def remove(session: Any, group: str, key: str) -> None:
    selected(session, group, key)
    install(session, **{group: tuple(r for r in getattr(state(session), group) if r.id != key)})
