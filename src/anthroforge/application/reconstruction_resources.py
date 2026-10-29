"""Reachability for embedded stage assets and shared variant/checkpoint snapshots."""

from typing import Any


def retain(document: Any, groups: dict[str, set[str]]) -> None:
    from .resources import referenced

    state = document.reconstruction
    groups["meshes"].update(row.asset for row in (*state.stages, *state.regions) if row.asset)
    for snapshot in state.snapshots:
        for kind, keys in referenced(snapshot.scene).items():
            groups[kind].update(keys)
