"""Selective reconstruction metadata transfer with explicit identity and resource ownership."""

import zipfile
from dataclasses import fields, replace
from typing import Any
from uuid import uuid4

from anthroforge.core.reconstruction import Reconstruction

from . import assembly_resources
from .assembly_source import cancelled


def selected(state: Any, subjects: set[str], variants: set[str]) -> Reconstruction:
    contexts = {""} | variants
    stages = tuple(s for s in state.stages if s.subject in subjects and s.variant in contexts)
    regions = tuple(r for r in state.regions if r.target in subjects and r.variant in contexts)
    reviews = tuple(r for r in state.reviews if r.subject in subjects and r.variant in contexts)
    assignments = tuple(a for a in state.assignments if a.target in subjects)
    return related(state, subjects, stages, regions, reviews, assignments)


def related(
    state: Any, subjects: Any, stages: Any, regions: Any, reviews: Any, assignments: Any
) -> Reconstruction:
    types = {a.type_id for a in assignments}
    evidence = {k for r in reviews for k in r.evidence}
    return Reconstruction(
        stages=stages,
        regions=regions,
        reviews=reviews,
        assignments=assignments,
        types=tuple(t for t in state.types if t.id in types),
        evidence=tuple(e for e in state.evidence if e.id in evidence),
        collections=collections(state, subjects | {r.id for r in regions}),
    )


def collections(state: Any, members: set[str]) -> tuple[Any, ...]:
    return tuple(
        replace(c, members=tuple(k for k in c.members if k in members))
        for c in state.collections
        if members.intersection(c.members)
    )


def copy(preparation: Any) -> Reconstruction:
    from . import assembly_variants

    p = preparation
    keys = set(p.options.get("variants", ()))
    state = selected(p.source.document.reconstruction, set(p.selection.records), keys)
    mapping = identities(state, p.ids)
    variants = assembly_variants.copy(p, keys, mapping)
    load_resources(p, state)
    changes = {
        f.name: tuple(remap(row, mapping, p.assets) for row in getattr(state, f.name))
        for f in fields(state)
        if f.name not in {"variants", "snapshots"}
    }
    return replace(variants, **changes)


def identities(state: Any, anatomy: dict[str, str]) -> dict[str, str]:
    mapping = dict(anatomy)
    for group in fields(state):
        for row in getattr(state, group.name):
            if hasattr(row, "id"):
                mapping[row.id] = str(uuid4())
    return mapping


def remap(row: Any, ids: Any, assets: Any) -> Any:
    scalar = {"id", "target", "subject", "type_id", "variant", "stage", "region"}
    arrays = {"members", "evidence"}
    values = {}
    for field in fields(row):
        value = getattr(row, field.name)
        if field.name in scalar:
            values[field.name] = ids.get(value, value)
        elif field.name in arrays:
            values[field.name] = tuple(ids.get(k, k) for k in value)
        elif field.name in {"asset", "resource"}:
            values[field.name] = assets[value]
    return replace(row, **values)


def load_resources(p: Any, state: Any) -> None:
    groups = dict(
        meshes={r.asset for r in (*state.stages, *state.regions)},
        evidence={r.resource for r in state.evidence},
    )
    with zipfile.ZipFile(p.source.path) as archive:
        for kind, keys in groups.items():
            for key in keys - p.assets.keys():
                cancelled(p.cancel)
                value = assembly_resources.read_one(archive, p.source.metadata, p.engine, kind, key)
                p.assets[key] = str(uuid4())
                getattr(p.resources, kind)[p.assets[key]] = value


def merge(before: Reconstruction, additions: Reconstruction) -> Reconstruction:
    return Reconstruction(
        **{f.name: (*getattr(before, f.name), *getattr(additions, f.name)) for f in fields(before)}
    )
