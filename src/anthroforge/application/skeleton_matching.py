"""Identity/provenance matching; bone names never establish a correspondence."""

from typing import Any

from anthroforge.core.skeleton_update import BoneMatch, validate_matches


def origins(document: Any, key: str) -> set[tuple[str, str]]:
    found = {(str(document.id), key)}
    for receipt in document.imports:
        found.update(
            (receipt.source_document, source)
            for source, copied in receipt.identities
            if copied == key
        )
    return found


def candidates(source: Any, destination: Any) -> dict[str, tuple[str, ...]]:
    indexed: dict[tuple[str, str], set[str]] = {}
    for bone in destination.entities:
        for origin in origins(destination, bone.id):
            indexed.setdefault(origin, set()).add(bone.id)
    return {
        bone.id: tuple(
            sorted(set().union(*(indexed.get(o, set()) for o in origins(source, bone.id))))
        )
        for bone in source.entities
    }


def inventory(source: Any, destination: Any) -> list[dict[str, Any]]:
    found = candidates(source, destination)
    counts: dict[str, int] = {}
    for values in found.values():
        for key in values:
            counts[key] = counts.get(key, 0) + 1
    return [row(bone, found[bone.id], counts) for bone in source.entities]


def row(bone: Any, matches: tuple[str, ...], counts: dict[str, int]) -> dict[str, Any]:
    selected = matches[0] if len(matches) == 1 and counts[matches[0]] == 1 else ""
    return dict(
        source=bone.id,
        name=bone.name,
        parent=bone.parent,
        candidates=matches,
        suggested=selected,
        reason="identity/provenance" if selected else "Choose a match",
    )


def parse(source: Any, destination: Any, matches: Any) -> tuple[BoneMatch, ...]:
    rows = (
        matches.items()
        if isinstance(matches, dict)
        else ((r["source"], r["target"]) for r in matches)
    )
    result = tuple(BoneMatch(str(a), str(b)) for a, b in rows)
    validate_matches(result)
    for value in result:
        source.entity(value.source)
        destination.entity(value.target)
    return result
