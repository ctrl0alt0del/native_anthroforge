"""Plane revisions are inputs to complete symmetric source constructions."""

from typing import Any

from .results import Port


def inputs(item: Any) -> set[Port]:
    half = getattr(item, "symmetric", None)
    if getattr(item, "mirrored_rows", False):
        half = item.mirror_plane
    return {Port(half.rule, "mirror")} if half and half.rule else set()
