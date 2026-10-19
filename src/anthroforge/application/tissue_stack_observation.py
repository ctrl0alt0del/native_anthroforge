"""Candidate observations invalidate plans without creating anatomical prerequisites."""

from typing import Any

from anthroforge.core.results import Port
from anthroforge.core.tissues import TissueVCP

from .tissue_stack_scene import participants


def membership(document: Any) -> tuple[str, ...]:
    return tuple(sorted(item.id for item in participants(document)))


def signature(item: TissueVCP) -> tuple[Any, ...]:
    return (
        item.stacking,
        item.intrinsic_material,
        item.final_result.asset,
        item.intrinsic_result.error,
        item.final_result.error,
        item.stack_relationships,
    )


def changed(session: Any, before: Any) -> None:

    old = {o.id: signature(o) for o in before.objects if isinstance(o, TissueVCP)}
    current = {o.id: signature(o) for o in session.document.objects if isinstance(o, TissueVCP)}
    changes = {key for key in old.keys() | current.keys() if old.get(key) != current.get(key)}
    if not changes:
        return
    targets = affected(session.document, changes, old, current)
    invalidate(session, targets)


def invalidate(session: Any, targets: set[str]) -> None:
    from . import tissue_results, tissue_tasks

    ports = {Port(key, phase) for key in targets for phase in ("plan", "final")}
    session.scheduler.invalidate_ports(ports, reason="stacking_candidate_output_changed")
    for key in targets:
        tissue_results.install(
            session, tissue_results.pending(session.document.object(key), {"plan", "final"})
        )
    tissue_tasks.schedule(session, targets, released=session.history.before is None)


def affected(document: Any, changes: set[str], old: Any, current: Any) -> set[str]:
    targets = {o.id for o in document.objects if isinstance(o, TissueVCP) and o.stacking}
    for key in changes:
        if (
            key in old
            and key in current
            and old[key][:2] == current[key][:2]
            and old[key][3] == current[key][3]
        ):
            targets.discard(key)
    return targets


def ports(document: Any, target: str, phase: str) -> set[Port]:
    if phase not in ("plan", "final") or not document.object(target).stacking:
        return set()
    outputs = ("intrinsic", "plan", "final") if phase == "final" else ("intrinsic",)
    values = {
        Port(item.id, output)
        for item in participants(document)
        for output in outputs
        if item.id != target
    }
    if phase == "final":
        values |= {
            Port(item.id, output) for item in document.entities for output in ("geometry", "pose")
        }
    return values | {Port(target, "stack_scope")}
