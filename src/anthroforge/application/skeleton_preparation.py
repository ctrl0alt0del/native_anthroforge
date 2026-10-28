"""Prepare, evaluate and compare a whole skeleton without touching the live document."""

from dataclasses import replace
from typing import Any

from anthroforge.core.results import Port

from . import (
    assembly_copy,
    candidate_dependencies,
    candidate_formulas,
    candidate_skin,
    comparison_geometry,
    skeleton_bindings,
    skeleton_candidate,
    skeleton_controls,
    skeleton_graph,
)
from .candidate_evaluation import EvaluationContext


def prepare(
    source: Any, options: Any, engine: Any, profiler: Any, payload: Any, cancel: Any
) -> Any:
    document, resources, preferences = payload
    p = skeleton_graph.copy(source, document, resources, engine, cancel, options)
    owned = resources.snapshot()
    for kind in owned.__dataclass_fields__:
        getattr(owned, kind).update(getattr(p.resources, kind))
    candidate = skeleton_graph.merge(document, p.values, tuple(p.mapping.references))
    context = EvaluationContext(engine, candidate, owned, preferences, cancel, profiler, document)
    context.fixed_poses = frozenset(item.id for item in p.values["entities"])
    context.options = options
    context.findings.extend(skeleton_graph.findings(p))
    return assess(context, p, options)


def assess(context: Any, p: Any, options: Any) -> Any:
    seeds = {Port(key, name) for key in context.fixed_poses for name in ("pose", "geometry")}
    skeleton_controls.reconcile(context, p, options)
    if not any(f.blocking for f in context.findings):
        review_formulas(context, p)
    if not any(f.blocking for f in context.findings):
        evaluate_construction(context, p, seeds)
    changes = skeleton_bindings.changes(context, p)
    evidence = []
    if not any(f.blocking for f in context.findings):
        evidence += skeleton_bindings.capture_bones(context, changes, options)
        evidence += skeleton_bindings.rebind_dependents(context, changes, options)
    if not any(f.blocking for f in context.findings):
        candidate_dependencies.evaluate(context, seeds)
    return completed(context, p, seeds, changes, evidence)


def review_formulas(context: Any, p: Any) -> None:
    from . import formula_inputs, property_guards

    try:
        property_guards.validate_writers(context.document)
    except ValueError as error:
        writer_conflict(context, str(error))
        return
    records = formula_inputs.formulas(context.document)
    keys = {k for k, (_, f) in records.items() if f.target.target in set(p.ids.values())}
    if keys:
        candidate_formulas.evaluate(context, keys, review=True)


def writer_conflict(context: Any, message: str) -> None:
    from anthroforge.core.skeleton_update import Finding

    context.findings.append(Finding("writers", "", message, blocking=True, kind="property"))


def evaluate_construction(context: Any, p: Any, seeds: Any) -> None:
    from anthroforge.core.object_outputs import output

    imported = {p.ids[key] for key in p.selection.records}
    inputs = {
        Port(key, output(context.document.object(key)))
        for key in imported
        if key in context.document.registry.construction
    }
    candidate_dependencies.evaluate(context, seeds | inputs, imported)


def completed(context: Any, p: Any, seeds: Any, changes: Any, evidence: Any) -> Any:
    skin = candidate_skin.assess(context, changes)
    provenance = assembly_copy.provenance(p.source, p.ids)
    context.document = replace(context.document, imports=(*context.document.imports, provenance))
    reads = skeleton_candidate.reads(context, seeds, p.mapping.reads)
    return bundle(context, p, reads, changes, evidence, skin)


def bundle(context: Any, p: Any, reads: Any, changes: Any, evidence: Any, skin: Any) -> Any:
    return skeleton_candidate.Candidate(
        context.baseline,
        context.document,
        context.resources,
        reads,
        p.ids,
        changes,
        tuple(context.findings),
        frozenset(context.prepared),
        tuple(evidence),
        comparison=compare(context),
        skin=skin,
    )


def compare(context: Any) -> dict[str, Any]:
    from .inspection_context import InspectionContext

    def frozen(document: Any) -> Any:
        return InspectionContext(
            document, context.resources, context.engine, document.workspaces[0]
        )

    return comparison_geometry.compare(
        frozen(context.baseline), frozen(context.document), context.cancel.handle
    )
