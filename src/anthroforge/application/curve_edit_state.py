"""Resolved editing is a query; only an explicit edit authors a retained baseline."""

from dataclasses import replace
from typing import Any, cast

from anthroforge.core.construction import Curve
from anthroforge.core.curve_shapes import binding_shape
from anthroforge.core.fibers import Fiber, FiberEdit

from .attachment_candidates import eligible


def current(session: Any, item: Any) -> Any:
    if not isinstance(item, Curve) or getattr(item, "edit", None):
        return item
    if not isinstance(item, Fiber) and not any(p.junction for p in item.points):
        return item
    if not isinstance(item, Fiber) and item.construction_revision != item.result.authored_revision:
        return item  # Accepted geometry cannot erase unpublished authored identities or points.
    asset = session.resources.paths.get(item.result.asset)
    return replace(item, points=asset.authored.points) if asset else item


def prepare[T](session: Any, before: Any, changed: T) -> T:
    from .parametric_policy import require_change

    require_change(session.document, before, changed)
    if not isinstance(before, Fiber) or not isinstance(changed, Fiber):
        return changed
    bindings_changed = binding_shape(before) != binding_shape(changed)
    if not shape_changed(before, changed) and not bindings_changed:
        return changed
    if not shape_changed(current(session, before), changed) and not bindings_changed:
        return cast(T, retain_geometry(before, changed))
    return cast(T, prepare_fiber(session, before, changed))


def prepare_fiber(session: Any, before: Fiber, changed: Fiber) -> Fiber:
    opening = current(session, before)
    edit = before.edit or baseline(session, before)
    targets = set(edit.candidates) | {b.reference for b in changed.bindings}
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
    return geometry_points(before) != geometry_points(after) or any(
        getattr(before, name) != getattr(after, name) for name in ("engine_settings", "closed")
    )


def geometry_points(curve: Curve) -> tuple[Any, ...]:
    return tuple(replace(p, stacking_fixed=False, protected_crease=False) for p in curve.points)


def retain_geometry(before: Fiber, changed: Fiber) -> Fiber:
    metadata = {p.id: p for p in changed.points}
    points = tuple(
        replace(
            p,
            stacking_fixed=metadata[p.id].stacking_fixed,
            protected_crease=metadata[p.id].protected_crease,
        )
        for p in before.points
    )
    return replace(changed, points=points)


def baseline(session: Any, item: Fiber) -> FiberEdit:
    if item.result.asset not in session.resources.paths:
        raise ValueError("Fiber editing needs its last accepted path.")
    return FiberEdit(item.result.asset, eligible(session.document, item.id), shape=False)
