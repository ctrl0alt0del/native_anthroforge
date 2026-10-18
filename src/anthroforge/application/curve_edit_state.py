"""Resolved editing is a query; only an explicit edit authors a retained baseline."""

from dataclasses import replace
from typing import Any, cast

from anthroforge.core.construction import Curve
from anthroforge.core.curve_shapes import binding_shape
from anthroforge.core.fibers import Fiber, FiberEdit

from .attachment_candidates import eligible


def current(session: Any, item: Any) -> Any:
    if not isinstance(item, Fiber) or item.edit:
        return item
    asset = session.resources.paths.get(item.result.asset)
    return replace(item, points=asset.authored.points) if asset else item


def prepare[T](session: Any, before: Any, changed: T) -> T:
    if not isinstance(before, Fiber) or not isinstance(changed, Fiber):
        return changed
    bindings_changed = binding_shape(before) != binding_shape(changed)
    if not shape_changed(before, changed) and not bindings_changed:
        return changed
    if not shape_changed(current(session, before), changed) and not bindings_changed:
        return cast(T, replace(changed, points=before.points))
    return cast(T, prepare_fiber(session, before, changed))


def prepare_fiber(session: Any, before: Fiber, changed: Fiber) -> Fiber:
    opening = current(session, before)
    edit = before.edit or baseline(session, before)
    targets = set(edit.candidates) | {b.target for b in changed.bindings}
    edit = replace(
        edit,
        candidates=tuple(sorted(targets)),
        rebind=tuple(sorted(set(edit.rebind) | moved_anchors(opening, changed))),
        shape=edit.shape or shape_changed(opening, changed),
    )
    return replace(changed, edit=edit)


def moved_anchors(before: Fiber, after: Fiber) -> set[str]:
    previous = {p.id: p for p in before.points}
    bound = {b.point for b in after.bindings}
    return {
        p.id
        for p in after.points
        if p.id in bound and (p.id not in previous or p.position != previous[p.id].position)
    }


def shape_changed(before: Curve, after: Curve) -> bool:
    return any(
        getattr(before, name) != getattr(after, name)
        for name in ("points", "engine_settings", "closed")
    )


def baseline(session: Any, item: Fiber) -> FiberEdit:
    if item.result.asset not in session.resources.paths:
        raise ValueError("Fiber editing needs its last accepted path.")
    return FiberEdit(item.result.asset, eligible(session.document, item.id), shape=False)
