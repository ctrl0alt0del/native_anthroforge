"""Selected-anatomy copy-on-write graphs over the existing typed assembly contracts."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.reconstruction import EditingScope

from . import assembly_copy, assembly_graph, assembly_resources, assembly_selection
from .editing_contexts import bare
from .resources import references
from .skeleton_graph import merge_records


def selection(document: Any, subjects: list[str]) -> Any:
    selected = set(subjects)
    if not selected or selected - document.registry.anatomy.keys():
        raise ValueError("Select authored SCPs or tissues for a variant.")
    reasons = {key: "Selected anatomy" for key in selected}
    assembly_selection.complete_sources(document, reasons)
    records = {key: document.object(key) for key in reasons}
    junctions = assembly_selection.selected_junctions(document, records)
    return assembly_selection.selection_records(document, records, reasons, junctions)


def duplicate(document: Any, resources: Any, subjects: list[str]) -> Any:
    picked = selection(document, subjects)
    ids = assembly_graph.identities(picked)
    ids.update({key: key for key in subjects})
    assets = copied_metadata(document, resources, picked, ids)
    values = assembly_copy.additions(document, picked, ids, assets)
    drivers(document, picked, values, ids)
    changes = merged_groups(document, values)
    editable = tuple(sorted(ids[key] for key in picked.records))
    scope = EditingScope(
        frozenset(ids.values()), frozenset(document.registry.records) - set(editable)
    )
    copied = replace(bare(document), editing_scope=scope, **changes)
    return copied, editable, tuple(sorted(ids.items()))


def merged_groups(document: Any, values: Any) -> dict[str, Any]:
    return {key: merge_records(getattr(document, key), rows) for key, rows in values.items()}


def copied_metadata(document: Any, resources: Any, selection: Any, ids: Any) -> dict[str, str]:
    source = assembly_copy.source_records(document, selection)
    required = references(source["entities"], source["objects"])
    complete_metadata(resources, required)
    pending = {(kind, key) for kind in ("paths", "attachments") for key in required[kind]}
    mapping = {key: str(uuid4()) for _, key in pending}
    for kind, key in pending:
        value = getattr(resources, kind)[key]
        getattr(resources, kind)[mapping[key]] = assembly_resources.remapped(
            value, kind, ids, mapping
        )
    return mapping


def complete_metadata(resources: Any, found: Any) -> None:
    visited: set[tuple[str, str]] = set()
    while pending := {(k, v) for k, rows in found.items() for v in rows} - visited:
        visited |= pending
        for kind, key in pending:
            if kind == "paths":
                nested = references((), (resources.paths[key].authored,))
                for group, values in nested.items():
                    found[group] |= values
            if kind == "attachments":
                found["meshes"].update(t.material_asset for t in resources.attachments[key].targets)


def drivers(document: Any, selection: Any, values: Any, ids: Any) -> None:
    targets = set(selection.records)
    cloned = {row.id for row in selection.drivers}
    replacements = tuple(
        filtered(row, targets, False) for row in document.driving_shortcuts if row.id in cloned
    )
    copies = tuple(
        filtered(row, {ids[k] for k in targets}, True) for row in values["driving_shortcuts"]
    )
    values["driving_shortcuts"] = replacements + copies
    old = {f.id for row in replacements for f in row.formulas}
    mapped = {f.id for row in copies for f in row.formulas}
    values["formula_results"] = tuple(
        r for r in values["formula_results"] if r.formula in mapped | old
    )


def filtered(driver: Any, targets: set[str], included: bool) -> Any:
    return replace(
        driver,
        formulas=tuple(
            formula for formula in driver.formulas if (formula.target.target in targets) == included
        ),
    )
