"""Prepare, evaluate and compare a whole skeleton without touching the live document."""

from dataclasses import replace
from typing import Any

from anthroforge.core.results import Port

from . import (
    assembly_copy,
    candidate_dependencies,
    comparison_geometry,
    skeleton_bindings,
    skeleton_candidate,
    skeleton_graph,
    skin_status,
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
    context.findings.extend(skeleton_graph.findings(p))
    return assess(context, p, options)


def assess(context: Any, p: Any, options: Any) -> Any:
    seeds = {Port(key, name) for key in context.fixed_poses for name in ("pose", "geometry")}
    if not context.findings:
        evaluate_construction(context, p, seeds)
    changes = skeleton_bindings.changes(context, p)
    evidence = []
    if not any(f.blocking for f in context.findings):
        evidence += skeleton_bindings.capture_bones(context, changes, options)
        evidence += skeleton_bindings.rebind_dependents(context, changes, options)
    if not any(f.blocking for f in context.findings):
        candidate_dependencies.evaluate(context, seeds)
    return completed(context, p, seeds, changes, evidence)


def evaluate_construction(context: Any, p: Any, seeds: Any) -> None:
    imported = {p.ids[key] for key in p.selection.records}
    inputs = {
        Port(key, "path") for key in imported if key in context.document.registry.construction
    }
    candidate_dependencies.evaluate(context, seeds | inputs, imported)


def completed(context: Any, p: Any, seeds: Any, changes: Any, evidence: Any) -> Any:
    provenance = assembly_copy.provenance(p.source, p.ids)
    context.document = replace(context.document, imports=(*context.document.imports, provenance))
    reads = skeleton_candidate.reads(context, seeds, p.mapping.reads)
    return bundle(context, p, reads, changes, evidence)


def bundle(context: Any, p: Any, reads: Any, changes: Any, evidence: Any) -> Any:
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
        skin=skin_impact(context),
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


def skin_impact(context: Any) -> dict[str, Any]:
    status = skin_status.assess(context.document, context.resources)
    return dict(
        available=status.operations["update"].available,
        reason=status.operations["update"].reason,
        previewed=False,
    )
