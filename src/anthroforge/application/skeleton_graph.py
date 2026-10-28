"""Identity-preserving bone replacement over the shared typed graph-copy adapters."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.entities import SCP
from anthroforge.core.skeleton_update import Finding
from anthroforge.core.tissues import TissueVCP

from . import (
    assembly_graph,
    assembly_resources,
    assembly_selection,
    entity_revisions,
    skeleton_correspondence,
    skeleton_mirrors,
)
from .assembly_mapping import Mappings
from .assembly_preparation import Preparation
from .skeleton_matching import parse


def selection(document: Any, keys: set[str]) -> Any:
    reasons = {key: "Replacement bone" for key in keys}
    for key in keys:
        document.object(key)
    assembly_selection.complete_sources(document, reasons)
    records = {key: document.object(key) for key in reasons}
    if any(isinstance(item, TissueVCP) for item in records.values()):
        raise ValueError("Map tissue supports explicitly; skeleton updates do not import tissues.")
    junctions = assembly_selection.selected_junctions(document, records)
    value = assembly_selection.selection_records(document, records, reasons, junctions)
    return replace(value, shortcuts=())


def copy(
    source: Any, destination: Any, resources: Any, engine: Any, cancel: Any, options: Any
) -> Any:
    matches = parse(source.document, destination, options.get("matches", {}))
    additions = options.get("additions", {})
    keys = {m.source for m in matches} | set(additions)
    if not keys or {m.source for m in matches} & set(additions):
        raise ValueError("Choose distinct matched bones or explicit additions.")
    p = Preparation(source, destination, resources, engine, cancel, options)
    p.selection = expanded(source.document, keys, options.get("mappings", {}))
    allocate(p, matches)
    p.copy_records()
    retain_destination(p, matches, additions)
    return p


def expanded(document: Any, keys: set[str], mappings: Any) -> Any:
    seeds = set(keys)
    while True:
        picked = selection(document, seeds)
        rows = assembly_graph.boundaries(document, picked)
        additions = assembly_graph.included_decisions(mappings, rows) - seeds
        if any(key in document.index.entities for key in additions):
            raise ValueError("Choose a destination match or an explicit parent for added bones.")
        if not additions:
            return picked
        seeds.update(additions)


def allocate(p: Any, matches: Any) -> None:
    p.loaded = assembly_resources.load(p.source, p.selection, p.engine, p.cancel)
    p.ids = assembly_graph.identities(p.selection, p.loaded)
    p.ids.update({m.source: m.target for m in matches})
    retain_driver_ids(p)
    p.mapping = Mappings(p.source, p.destination, p.ids, p.options.get("mappings", {}))
    skeleton_mirrors.map_rules(p)
    rows = assembly_graph.boundaries(p.source.document, p.selection)
    p.mapping.assess(tuple(r for r in rows if r.relationship != "mirror"))
    p.resources, p.assets = assembly_resources.transfer(p.loaded, p.ids)
    assembly_resources.restore_legacy_inputs(p)


def retain_destination(p: Any, matches: Any, additions: Any) -> None:
    paired = {m.target for m in matches}
    parents = {p.ids[key]: value for key, value in additions.items()}
    p.values["entities"] = tuple(
        replacement(p.destination.entity(item.id), item)
        if item.id in paired
        else added(p, item, parents)
        for item in p.values["entities"]
    )
    p.values.pop("mirror_rules", None)
    p.values.pop("shared_mirror_targets", None)
    p.values.pop("shortcuts", None)
    retain_drivers(p)


def retain_drivers(p: Any) -> None:
    retained = {d.id for d in p.destination.driving_shortcuts}
    p.values["driving_shortcuts"] = tuple(
        replace(d, exposed=False) for d in p.values["driving_shortcuts"] if d.id not in retained
    )
    kept = {f.id for d in p.values["driving_shortcuts"] for f in d.formulas}
    p.values["formula_results"] = tuple(r for r in p.values["formula_results"] if r.formula in kept)


def retain_driver_ids(p: Any) -> None:
    verified = skeleton_correspondence.identities(p.source.document, p.destination)
    for driver in p.selection.drivers:
        for key in graph_records.owned(driver):
            if key in verified:
                p.ids[key] = verified[key]


def replacement(before: SCP, source: SCP) -> SCP:
    fields = ("primitive", "deformers", "thickness", "matrix", "geometry_offset", "asset", "result")
    changes = {key: getattr(source, key) for key in fields}
    item = replace(before, **changes, pose_receipt=None, status="ready", error="")
    return entity_revisions.authored(before, item)


def added(p: Any, item: SCP, parents: Any) -> SCP:
    from .assembly_copy import root_parent

    parent = parents.get(item.id, "")
    if not parent:
        raise ValueError("Each added bone requires an explicit destination parent.")
    p.destination.entity(parent)
    return root_parent(item, parent)


def merge(document: Any, values: Any, references: Any = ()) -> Any:
    changes = {
        group: merge_records(getattr(document, group), rows) for group, rows in values.items()
    }
    changes["external_references"] = (*document.external_references, *references)
    return replace(document, **changes)


def merge_records(before: tuple[Any, ...], incoming: tuple[Any, ...]) -> tuple[Any, ...]:
    replacements = {identity(item): item for item in incoming}
    existing = {identity(item) for item in before}
    return tuple(replacements.get(identity(item), item) for item in before) + tuple(
        item for item in incoming if identity(item) not in existing
    )


def identity(item: Any) -> str:
    return str(getattr(item, "id", getattr(item, "formula", "")))


def findings(p: Any) -> tuple[Finding, ...]:
    blocked = [Finding(r["reference"], "", r["message"], blocking=True) for r in p.mapping.findings]
    blocked.extend(
        Finding("reference:" + row.id, "", "Map required reference: " + row.name, blocking=True)
        for row in p.mapping.references
        if not row.target
    )
    return tuple(blocked)


def remap_property(reference: Any, mapping: dict[str, str]) -> Any:
    return graph_records.rewritten(reference, mapping)
