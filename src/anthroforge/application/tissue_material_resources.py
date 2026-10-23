"""Accepted material snapshots retain their own geometry and constraint captures."""

from collections.abc import Iterable

from anthroforge.core.object_registry import Authored
from anthroforge.core.tissues import TissueVCP


def retain(objects: Iterable[Authored], groups: dict[str, set[str]]) -> None:
    for item in objects:
        if not isinstance(item, TissueVCP):
            continue
        for state in (item.rest_material, item.intrinsic_material, item.final_material):
            if state is None:
                continue
            groups["meshes"].update((state.rest, state.own, state.final, state.crop_base))
            if state.base_state.kind in ("SURFACE", "CURVE"):
                groups["meshes" if state.base_state.kind == "SURFACE" else "paths"].add(state.base)
            groups["meshes"].update(row.material_asset for row in state.constraints)
            groups["bindings"].update(row.binding_asset for row in state.constraints)
