"""Variant candidates reuse production dependency, attachment and comparison evaluators."""

from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.object_outputs import output
from anthroforge.core.results import Port, geometry_asset
from anthroforge.core.skeleton_update import BoneChange
from anthroforge.native import topology

from . import (
    candidate_dependencies,
    candidate_skin,
    skeleton_bindings,
    skeleton_candidate,
    skeleton_comparison,
    skeleton_placements,
    variant_reconciliation,
)
from .candidate_evaluation import EvaluationContext


def prepare(engine: Any, profiler: Any, request: Any, payload: Any, cancel: Any) -> Any:
    accepted, resources, preferences = payload
    record, baseline, current, mode, options = request
    document, findings = proposed(record, baseline, current, accepted, mode, options)
    previous = current if mode == "refresh" else accepted
    context = EvaluationContext(
        engine, document, resources, preferences, cancel, profiler, previous
    )
    context.options = skeleton_placements.normalized(document, options)
    context.findings.extend(findings)
    return evaluate(context, record, baseline, current, mode)


def proposed(
    record: Any, baseline: Any, current: Any, accepted: Any, mode: str, options: Any
) -> Any:
    if mode == "refresh":
        return variant_reconciliation.refreshed(record, baseline, current, accepted), []
    return variant_reconciliation.merge(
        record, baseline, current, accepted, options.get("choices", {})
    )


def evaluate(context: Any, record: Any, baseline: Any, current: Any, mode: str) -> Any:
    owners = variant_reconciliation.scope(record, baseline, current)
    seeds = seeds_for(context.document, owners)
    changes = changed_surfaces(
        context, owners if mode == "promote" else set(context.document.registry.anatomy)
    )
    context.fixed_poses = (
        frozenset(k for k in record.subjects if k in context.document.index.entities)
        if mode == "promote"
        else frozenset()
    )
    evidence = prepare_bindings(context, changes)
    if not any(row.blocking for row in context.findings):
        candidate_dependencies.evaluate(context, seeds, owners if mode == "refresh" else None)
    return bundle(context, owners, seeds, changes, evidence)


def seeds_for(document: Any, owners: set[str]) -> set[Port]:
    seeds = {Port(k, output(document.object(k))) for k in owners if k in document.registry.records}
    seeds.update(Port(k, "pose") for k in owners if k in document.index.entities)
    seeds.update(
        Port(f.id, "formula")
        for d in document.driving_shortcuts
        if d.id in owners
        for f in d.formulas
    )
    return seeds


def changed_surfaces(context: Any, owners: set[str]) -> tuple[Any, ...]:
    rows = []
    for key in sorted(owners & context.document.registry.anatomy.keys()):
        old, new = context.baseline.registry.records.get(key), context.document.object(key)
        if old is new:
            continue
        compatible = correspondence(context, old, new)
        placement = isinstance(new, SCP) and (old is None or new.matrix != old.matrix)
        rows.append(
            BoneChange(
                key, key, placement, True, "verified" if compatible else "unverified", old is None
            )
        )
    return tuple(rows)


def correspondence(context: Any, old: Any, new: Any) -> bool:
    a, b = geometry_asset(old) if old else "", geometry_asset(new)
    if not a or not b:
        return not a and not b
    if a == b:
        return True
    first, second = context.assets[a].mesh, context.assets[b].mesh
    return topology.same_content(first, second, context.cancel.handle)


def prepare_bindings(context: Any, changes: Any) -> list[Any]:
    bones = tuple(c for c in changes if c.target in context.fixed_poses)
    evidence = skeleton_bindings.capture_bones(context, bones, context.options)
    evidence += skeleton_bindings.rebind_dependents(context, changes, context.options)
    return evidence


def bundle(context: Any, owners: Any, seeds: Any, changes: Any, evidence: Any) -> Any:
    skin = candidate_skin.assess(context, changes)
    reads = skeleton_candidate.reads(
        context, seeds, owners & context.baseline.registry.records.keys()
    )
    evidence = skeleton_comparison.attachments(context, evidence)
    return result(context, reads, changes, evidence, skin)


def result(context: Any, reads: Any, changes: Any, evidence: Any, skin: Any) -> Any:
    return skeleton_candidate.Candidate(
        context.baseline,
        context.document,
        context.resources,
        reads,
        {},
        changes,
        tuple(context.findings),
        frozenset(context.prepared),
        tuple(evidence),
        comparison=skeleton_comparison.describe(context, changes),
        skin=skin,
        publication_resources=context.resources.selected(context.document),
    )
