"""Copy complete typed records and source results without reevaluating their geometry."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records
from anthroforge.core.assembly import ImportProvenance
from anthroforge.core.entities import SCP, Attachment

from . import assembly_graph, assembly_resources, assembly_selection
from .assembly_candidate import Candidate, ReadSet


def selected(source: Any, keys: list[str], attached: bool, mappings: Any) -> Any:
    seeds = set(keys)
    while True:
        selection = assembly_selection.expand(source.document, sorted(seeds), attached)
        rows = assembly_graph.boundaries(source.document, selection)
        additions = assembly_graph.included_decisions(mappings, rows) - seeds
        if not additions:
            return selection, rows
        seeds |= additions


def source_records(document: Any, selection: Any) -> dict[str, tuple[Any, ...]]:
    picked = set(selection.records)
    values = {
        name: tuple(v for v in getattr(document, name) if v.id in picked)
        for name in ("entities", "objects", "controls")
    }
    values.update(junctions=selection.junctions, driving_shortcuts=selection.drivers)
    values["shortcuts"] = selection.shortcuts
    formulas = {f.id for d in selection.drivers for f in d.formulas}
    values["formula_results"] = tuple(r for r in document.formula_results if r.formula in formulas)
    return values


def additions(document: Any, selection: Any, ids: Any, assets: Any) -> dict[str, tuple[Any, ...]]:
    return {
        key: graph_records.rewritten(rows, ids, assets)
        for key, rows in source_records(document, selection).items()
    }


def destination_parent(destination: Any, parent: str, required: bool) -> str:
    if not required:
        return ""
    if not destination.entities:
        if parent:
            raise ValueError("An empty anatomical hierarchy has no destination parent.")
        return ""
    parent = parent or next(e.id for e in destination.entities if not e.parent)
    destination.entity(parent)
    return parent


def hierarchy(values: Any, selection: Any, ids: Any, parent: str) -> None:
    roots = {ids[k] for k in assembly_graph.roots(selection)}
    if not roots:
        return
    group = SCP("Imported anatomy") if not parent and len(roots) > 1 else None
    parent = group.id if group else parent
    copied = tuple(root_parent(v, parent) if v.id in roots else v for v in values["entities"])
    values["entities"] = ((group,) if group else ()) + copied


def root_parent(item: SCP, parent: str) -> SCP:
    if item.parent == parent:
        return item
    return replace(
        item,
        parent=parent,
        attachment=Attachment(),
        pose_receipt=None,
        capture_parent_matrix=(),
        capture_parent_offset=(0.0, 0.0, 0.0),
    )


def provenance(source: Any, ids: Any, mappings: Any = ()) -> ImportProvenance:
    return ImportProvenance(
        str(uuid4()),
        str(source.document.id),
        source.document.revision,
        source.digest,
        source.document.name,
        tuple(sorted(ids.items())),
        tuple(mappings),
    )


def copy_closed(source: Any, destination: Any, keys: Any, engine: Any, cancel: Any) -> Candidate:
    selection, boundaries = selected(source, keys, False, {})
    if boundaries:
        raise ValueError("This graph has external references requiring mapping decisions.")
    source_resources = assembly_resources.load(source, selection, engine, cancel)
    ids = assembly_graph.identities(selection, source_resources)
    resources, assets = assembly_resources.transfer(source_resources, ids)
    values = additions(source.document, selection, ids, assets)
    parent = destination_parent(destination, "", bool(assembly_graph.roots(selection)))
    hierarchy(values, selection, ids, parent)
    empty = bool(assembly_graph.roots(selection)) and not destination.entities
    reads = ReadSet(str(destination.id), empty_hierarchy=empty)
    candidate = Candidate(values, resources, ids, provenance(source, ids), (), reads)
    candidate.merge(destination)
    return candidate
