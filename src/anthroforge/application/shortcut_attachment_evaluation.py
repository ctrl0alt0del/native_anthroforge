"""Temporary bindings are worker inputs, never replacements for authored settings."""

from dataclasses import replace
from typing import Any

from anthroforge.core import attachment_provenance
from anthroforge.core.results import Port
from anthroforge.native import shortcut_attachments

from .shortcut_capture import effective


def contexts(document: Any, targets: set[str]) -> tuple[Any, ...]:
    return tuple(c for c in document.shortcut_edits if set(c.targets) & targets)


def protected(document: Any, targets: set[str]) -> set[str]:
    return {b.target for c in contexts(document, targets) for b in c.bindings}


def extra_reads(document: Any, targets: set[str]) -> set[Port]:
    ports = set()
    for context in contexts(document, targets):
        if context.policy.backsolve and context.owner in targets:
            ports.add(Port(context.owner, "geometry"))
        for override in context.policy.descendants:
            child = document.entity(override.target)
            if (
                child.id in targets
                and effective(child.attachment, override).parent_mode == "SURFACE_NEAREST"
            ):
                ports.add(Port(child.parent, "geometry"))
    return ports


def contract(job: Any, document: Any, targets: set[str]) -> None:
    additional = extra_reads(document, targets)
    job.observes |= frozenset(additional)
    job.prerequisites |= frozenset(additional)
    job.provides = frozenset(output_ports(document, targets))


def output_ports(document: Any, targets: set[str]) -> set[Port]:
    owners = {c.owner for c in contexts(document, targets) if c.policy.backsolve}
    return {Port(key, "shortcut_pose" if key in owners else "pose") for key in targets}


def planning_graph(document: Any, targets: set[str]) -> dict[Port, set[Port]]:
    from . import dependencies

    original = dependencies.graph(document)
    graph = {key: set(value) for key, value in original.items() if key not in original.blocked}
    for port in output_ports(document, targets):
        base = Port(port.owner, "pose")
        if base in graph:
            graph[port] = graph[base] | extra_reads(document, {port.owner})
    return graph


def prepare(
    engine: Any, document: Any, entities: list[Any], meshes: Any, targets: set[str]
) -> tuple[list[Any], set[str]]:
    lookup = {v.id: v for v in entities}
    owners: set[str] = set()
    for context in contexts(document, targets):
        if context.status != "ready":
            raise ValueError(context.error or "Shortcut attachment preparation is pending.")
        for binding in context.bindings:
            child = lookup[binding.target]
            lookup[child.id] = replace(child, attachment=binding.attachment)
        if context.anchor and context.owner in targets:
            backsolve(engine, lookup, context, meshes, document)
            owners.add(context.owner)
    return [lookup[v.id] for v in entities], owners


def backsolve(engine: Any, lookup: Any, context: Any, meshes: Any, document: Any) -> None:
    from . import scp_surface_parents
    from anthroforge.native.attachments import reflected_parent

    child = lookup[context.owner]
    parent = lookup[child.parent]
    frame = scp_surface_parents.frame(document, child) if child.attachment.parent_instance else None
    parent = reflected_parent(engine, child, parent, frame)
    anchor = context.anchor
    retained = (anchor.mode, anchor.index, anchor.fallback, anchor.parent_local)
    matrix = shortcut_attachments.backsolve(engine, child, parent, meshes, retained)
    lookup[child.id] = replace(child, matrix=matrix, status="ready", error="")


def restore(document: Any, entities: list[Any], targets: set[str]) -> list[Any]:
    lookup = {v.id: v for v in entities}
    touched = {b.target for c in contexts(document, targets) for b in c.bindings}
    touched |= {c.owner for c in contexts(document, targets) if c.anchor}
    return [
        restored(document, lookup, item) if item.id in targets & touched else item
        for item in entities
    ]


def restored(document: Any, lookup: Any, item: Any) -> Any:
    original = document.entity(item.id)
    if not item.parent or item.status != "ready":
        return replace(item, attachment=original.attachment)
    restored_item = replace(item, attachment=original.attachment)
    from .scp_surface_parents import receipt as spatial_receipt

    receipt = spatial_receipt(document, restored_item, lookup[item.parent])
    if item.attachment != original.attachment:
        receipt = replace(receipt, effective=item.attachment)
    return replace(restored_item, pose_receipt=receipt)


def request(session: Any, keys: set[str] | None = None) -> None:
    from . import evaluation
    from .construction_policy import mode

    available = {c.id for c in session.document.shortcut_edits} if keys is None else keys
    targets: set[str] = set()
    for context in session.document.shortcut_edits:
        if context.id not in available or context.status != "ready":
            continue
        candidates = {v.target for v in context.bindings}
        if context.anchor:
            candidates.add(context.owner)
        targets.update(key for key in candidates if mode(session.document, key) != "MANUAL")
    if targets and session.document.attachments_enabled:
        evaluation.request(session, targets, recapture=set())
