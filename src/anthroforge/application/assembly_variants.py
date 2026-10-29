"""Opt-in alternative import reuses typed graph preparation for each retained scene."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.reconstruction import EditingScope, Reconstruction, SceneSnapshot

from .editing_contexts import bare
from .variant_reconciliation import record_ids


def copy(p: Any, keys: set[str], metadata_ids: dict[str, str]) -> Reconstruction:
    state, rows = p.source.document.reconstruction, []
    snapshots: list[SceneSnapshot] = []
    metadata_ids.update({key: str(uuid4()) for key in keys})
    for key in sorted(keys):
        original = state.variant(key)
        if set(original.subjects) - p.selection.records.keys():
            raise ValueError("Select all anatomy used by the included variant: " + original.name)
        baseline, first = snapshot(p, state.snapshot(original.baseline), p.ids)
        current, mapping = snapshot(p, state.snapshot(original.current), first)
        snapshots.extend((baseline, current))
        rows.append(variant(original, baseline, current, mapping, metadata_ids))
    return Reconstruction(variants=tuple(rows), snapshots=tuple(snapshots))


def snapshot(p: Any, document: Any, identities: Any) -> Any:
    worker = preparation(p, document, identities)
    candidate = worker.run(list(p.selection.records.keys() & document.registry.records.keys()))
    absorb(p, worker, candidate)
    scene = candidate.merge(p.destination)
    scope = copied_scope(document, scene, worker.ids)
    return SceneSnapshot(replace(bare(scene), editing_scope=scope)), worker.ids


def preparation(p: Any, document: Any, identities: Any) -> Any:
    from .assembly_preparation import Preparation

    source = replace(p.source, document=document)
    return Preparation(
        source,
        p.destination,
        p.available,
        p.engine,
        p.cancel,
        p.options,
        copy_reconstruction=False,
        identity_overrides=identities,
        source_cache=p.loaded,
    )


def copied_scope(source: Any, copied: Any, ids: Any) -> EditingScope | None:
    scope = source.editing_scope
    if scope is None:
        return None
    editable = frozenset(ids.get(key, key) for key in scope.editable if key in ids)
    return EditingScope(editable, frozenset(record_ids(copied)) - editable)


def absorb(p: Any, worker: Any, candidate: Any) -> None:
    p.mapping.findings.extend(candidate.findings)
    p.mapping.rows.extend(row for row in candidate.mappings if row not in p.mapping.rows)
    p.mapping.reads.update(worker.mapping.reads)
    for kind in candidate.resources.__dataclass_fields__:
        getattr(p.resources, kind).update(getattr(candidate.resources, kind))
    p.assets.update({key: value for key, value in worker.assets.items() if key not in p.assets})


def variant(original: Any, before: Any, after: Any, ids: Any, metadata_ids: Any) -> Any:
    mapping = tuple((ids.get(a, a), ids.get(b, b)) for a, b in original.construction_map)
    return replace(
        original,
        id=metadata_ids[original.id],
        baseline=before.id,
        current=after.id,
        parent=metadata_ids.get(original.parent, ""),
        subjects=tuple(ids[k] for k in original.subjects),
        editable=tuple(ids[k] for k in original.editable if k in ids),
        construction_map=mapping,
    )
