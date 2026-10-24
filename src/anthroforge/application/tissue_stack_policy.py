"""Translate persistent side relationships without inferring them from geometry proximity."""

from typing import Any

from anthroforge.native.stacking_abi import Policy, Settings

from . import mirror_stacking
from .tissue_stack_scene import identity


def settings(value: Any) -> Settings:
    return Settings(
        value.search,
        1e-10,
        1e-9,
        value.clearance,
        value.radius,
        value.strength,
        value.blend,
        value.preservation,
        value.adjustment,
        64 * 1024 * 1024,
        64 * 1024 * 1024,
        2000000,
    )


def policies(scene: Any) -> tuple[list[Any], list[Any]]:
    rows, unique = [], {}
    regions: list[Any] = []
    for item in scene.document.objects:
        for relation in getattr(item, "stack_relationships", ()):
            pair = available_pair(scene, item, relation)
            if pair is None:
                continue
            key = tuple(sorted(pair))
            if key in unique:
                raise ValueError("This side pair has conflicting duplicate stacking intent.")
            unique[key] = relation
            rows.append(policy(scene, relation, *pair, regions))
    return rows, regions


def available_pair(scene: Any, item: Any, relation: Any) -> tuple[int, int] | None:
    first, second = identity(item.id, relation.side), identity(relation.other, relation.other_side)
    if first in scene.domains and second in scene.domains:
        return first, second
    if relation.excluded:
        return None  # Negative intent needs no provider geometry and survives rule reactivation.
    if (item.id, relation.side) in scene.leases and (
        relation.other,
        relation.other_side,
    ) in scene.leases:
        return None
    if scene.target in (item.id, relation.other):
        raise ValueError("Stacking target unavailable; enable compatible surface tissues.")
    return None


def policy(scene: Any, relation: Any, first: int, second: int, regions: list[Any]) -> Policy:
    cover = 0 if relation.mode == "AUTO" else first if relation.cover == "SELF" else second
    offset = len(regions)
    invalid = selected_regions(scene, relation, cover, regions) if relation.regions else False
    return Policy(
        first,
        second,
        cover,
        relation.excluded,
        invalid,
        offset,
        len(regions) - offset,
        ("AUTO", "REQUESTED", "EXPLICIT").index(relation.mode),
    )


def selected_regions(scene: Any, relation: Any, cover: int, regions: list[Any]) -> bool:
    from .tissue_fields import mesh_domain

    owner, _ = scene.identities[cover]
    state = mirror_stacking.material(scene, owner)
    topology = mesh_domain(scene.resources.meshes[state.base].mesh)[1]
    parts = {key: i for i, key in enumerate(state.base_state.parts)}
    regions.extend((parts.get(part, 0), face) for part, face in relation.regions)
    return topology != relation.topology or any(part not in parts for part, _ in relation.regions)
