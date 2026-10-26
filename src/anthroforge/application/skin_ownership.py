"""Skin ownership follows anatomical bindings, preserving reflected target instances."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.points import Anchor
from anthroforge.core.skin_sources import Source
from anthroforge.core.surfaces import Surface
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.skin_capture import source_counts

from . import mirror_bindings


@dataclass(frozen=True)
class Supports:
    offsets: tuple[int, ...]
    bones: tuple[int, ...]
    candidates: tuple[tuple[int, ...], ...]
    warnings: tuple[str, ...]


def construction(item: Any) -> tuple[str, ...]:
    if isinstance(item, TissueVCP):
        return (item.source,)
    if isinstance(item, Surface):
        return tuple(use.curve for use in item.curves)
    return ()


def mapped_reference(document: Any, item: Any, rule: str, key: str, ref: Any) -> Any:
    return (
        mirror_bindings.counterpart(document, MirrorInstance(item.id, rule), key, ref)
        if rule
        else ref
    )


def targets(
    document: Any, owner: str, rule: str, warnings: set[str]
) -> tuple[tuple[str, str], ...]:
    item = document.object(owner)
    if not isinstance(item, (Fiber, Anchor)):
        return tuple((key, rule) for key in construction(item))
    result = []
    for key, ref in mirror_bindings.references(item):
        try:
            mapped = mapped_reference(document, item, rule, key, ref)
            result.append((mapped.target, mapped.instance))
        except ValueError as error:
            warnings.add(f"Skin ownership for {item.name}: {error}")
    return tuple(result)


def supports(document: Any, source: Source, warnings: set[str]) -> frozenset[Source]:
    pending, seen, found = [(source.owner, source.instance)], set(), set()
    while pending:
        owner, rule = pending.pop()
        if (owner, rule) in seen:
            continue
        seen.add((owner, rule))
        item = document.registry.records.get(owner)
        if isinstance(item, SCP):
            found.add(Source(owner, "SCP", rule))
        elif item is not None:
            pending.extend(targets(document, owner, rule, warnings))
        else:
            warnings.add("Skin ownership has a missing anatomical source: " + owner)
    return frozenset(found)


def offsets(rows: Any) -> tuple[int, ...]:
    values = [0]
    for row in rows:
        count = source_counts(row.mesh, False)[0]
        values.append(values[-1] + count)
    return tuple(values)


def source_candidates(document: Any, source: Any, indices: Any, warnings: Any) -> tuple[int, ...]:
    return tuple(
        sorted(indices[key] for key in supports(document, source, warnings) if key in indices)
    )


def capture(document: Any, rows: Any, owners: tuple[str, ...]) -> Supports:
    indices = {row.identity: i for i, row in enumerate(rows)}
    bone_ids = {key: i for i, key in enumerate(owners)}
    warnings: set[str] = set()
    candidates = tuple(source_candidates(document, row.identity, indices, warnings) for row in rows)
    bones = tuple(
        bone_ids.get(row.identity.owner, -1) if row.identity.kind == "SCP" else -1 for row in rows
    )
    return Supports(offsets(rows), bones, candidates, tuple(sorted(warnings)))
