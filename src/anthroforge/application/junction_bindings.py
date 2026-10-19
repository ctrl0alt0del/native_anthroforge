"""Junction binding edits share one authored owner and consume its accepted capture."""

from dataclasses import replace
from typing import Any

from anthroforge.core.fibers import Fiber, FiberBinding, FiberEdit
from anthroforge.core.junctions import PointRef, members

from . import consumed_paths, curve_edit_state
from .attachment_candidates import eligible


def binding(item: Any, point: str) -> FiberBinding | None:
    return (
        next((b for b in item.bindings if b.point == point), None)
        if isinstance(item, Fiber)
        else None
    )


def assigned(item: Any, point: str, value: FiberBinding | None) -> Any:
    if not isinstance(item, Fiber):
        return item
    values = {b.point: b for b in item.bindings if b.point != point}
    if value is not None:
        values[point] = replace(value, point=point)
    return replace(item, bindings=tuple(values[p.id] for p in item.points if p.id in values))


def share(session: Any, changes: Any, refs: Any, value: FiberBinding | None) -> None:
    for ref in refs:
        item = changes.get(ref.curve) or curve_edit_state.current(
            session, session.document.object(ref.curve)
        )
        changed = assigned(item, ref.point, value)
        if changed != item:
            changes[ref.curve] = changed


def joining(session: Any, changes: Any, refs: Any, source: PointRef) -> None:
    item = changes[source.curve]
    value = binding(item, source.point)
    if value is None and any(binding(changes[r.curve], r.point) for r in refs):
        raise ValueError("Choose the bound fiber point as the junction source.")
    share(session, changes, refs, value)


def expand(session: Any, changes: Any, result: Any) -> None:
    links = members(session.document.objects)
    sources = {j.id: j.source for j in session.document.junctions}
    for key, item in changes.items():
        before = session.document.object(key)
        if not isinstance(item, Fiber):
            continue
        for point in item.points:
            value = binding(item, point.id)
            if point.junction and value != binding(before, point.id):
                if value and not isinstance(
                    session.document.object(sources[point.junction].curve), Fiber
                ):
                    raise ValueError("Detach this junction before adding a fiber-only binding.")
                share(session, result, links[point.junction], value)


def accepted(document: Any, resources: Any, item: Fiber) -> tuple[Fiber, set[str]]:
    sources = {j.id: j.source for j in document.junctions}
    result, followers = item, set()
    for point in item.points:
        ref = sources.get(point.junction)
        if ref is None or ref == PointRef(item.id, point.id):
            continue
        source = consumed_paths.accepted(document, resources.paths, ref.curve).authored
        result = assigned(result, point.id, binding(source, ref.point))
        followers.add(point.id)
    return result, followers


def resolve(document: Any, resources: Any, item: Fiber) -> Fiber:
    if not document.junctions:
        return item
    changed, followers = accepted(document, resources, item)
    if changed.bindings == item.bindings and (item.edit is None or not followers):
        return item
    edit = item.edit or FiberEdit(item.result.asset, eligible(document, item.id), shape=False)
    targets = set(edit.candidates) | {b.target for b in changed.bindings}
    edit = replace(
        edit,
        candidates=tuple(sorted(targets)),
        rebind=tuple(p for p in edit.rebind if p not in followers),
    )
    return replace(changed, edit=edit)
