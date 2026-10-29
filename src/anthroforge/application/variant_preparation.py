"""Variant candidates reuse production dependency, attachment and comparison evaluators."""

from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.object_outputs import output
from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import BoneChange

from . import (
    candidate_dependencies,
    candidate_skin,
    skeleton_bindings,
    skeleton_candidate,
    skeleton_comparison,
    skeleton_placements,
    variant_correspondence,
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
    configure(context, owners, seeds, mode)
    evaluate_sources(context, owners, seeds, mode)
    affected = owners if mode == "promote" else set(context.document.registry.anatomy)
    changes = changed_surfaces(context, affected, record.construction_map)
    evidence = prepare_bindings(context, changes)
    if not any(row.blocking for row in context.findings):
        candidate_dependencies.evaluate(context, seeds, owners if mode == "refresh" else None)
    return bundle(context, owners, seeds, changes, evidence)


def configure(context: Any, owners: Any, seeds: Any, mode: str) -> None:
    from . import property_guards, skeleton_preparation

    context.category = "variant_" + mode
    context.required = frozenset(owners | {p.owner for p in seeds if p.output == "formula"})
    context.editable = frozenset(owners) if mode == "refresh" else None
    if mode == "promote":
        context.fixed_poses = frozenset(owners & context.document.index.entities.keys())
    try:
        property_guards.validate_writers(context.document)
    except ValueError as error:
        skeleton_preparation.writer_conflict(context, str(error))


def evaluate_sources(context: Any, owners: Any, seeds: Any, mode: str) -> None:
    if mode != "promote" or any(f.blocking for f in context.findings):
        return
    candidate_dependencies.evaluate(context, seeds, owners | set(context.required))


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


def changed_surfaces(context: Any, owners: set[str], pairs: Any) -> tuple[Any, ...]:
    rows = []
    mapping = {new: old for old, new in pairs}
    for key in sorted(owners & context.document.registry.anatomy.keys()):
        old, new = context.baseline.registry.records.get(key), context.document.object(key)
        if old is new:
            continue
        compatible = variant_correspondence.verified(context, old, new, mapping)
        placement = isinstance(new, SCP) and (old is None or new.matrix != old.matrix)
        rows.append(
            BoneChange(
                key, key, placement, True, "verified" if compatible else "unverified", old is None
            )
        )
    return tuple(rows)


def prepare_bindings(context: Any, changes: Any) -> list[Any]:
    if any(f.blocking for f in context.findings):
        return []
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
