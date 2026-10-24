"""Explicit support intent reuses current-shape binding capture and coordinated publication."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.fibers import Fiber

from . import attachment_candidates, curve_edit_state, object_codec, surface_providers
from .object_operations import editable, install


def selected(session: Any, curve: str) -> Fiber:
    item = session.document.object(curve)
    if not isinstance(item, Fiber):
        raise ValueError("Choose a Fiber to configure deformation supports.")
    return item


def configure(session: Any, curve: str, policy: dict[str, Any]) -> None:
    item = selected(session, curve)
    editable(session, curve)
    value = requested_policy(session, item, policy)
    if value == item.support_policy:
        return
    current = curve_edit_state.current(session, item)
    edit = item.edit or curve_edit_state.baseline(session, item)
    candidates = tuple(sorted(set(edit.candidates) | set(value.included)))
    install(
        session, replace(current, support_policy=value, edit=replace(edit, candidates=candidates))
    )


def requested_policy(session: Any, item: Fiber, data: dict[str, Any]) -> Any:
    value = object_codec.decode_support_policy(data)
    if set(value.excluded) & {b.reference for b in item.bindings}:
        raise ValueError("An anatomical pin's target is required; remove its binding first.")
    for ref in value.included:
        surface_providers.get(session.engine, session.document, session.assets, ref)
    return value


def inspect(session: Any, curve: str) -> dict[str, Any]:
    item = selected(session, curve)
    return dict(
        policy=asdict(item.support_policy),
        accepted=[asdict(s) for s in item.supports],
        candidates=[asdict(ref) for ref in attachment_candidates.eligible(session.document, curve)],
    )
