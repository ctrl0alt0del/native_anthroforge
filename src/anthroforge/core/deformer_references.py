"""Shared relationship policy for controls and geometry-driven deformers."""

from typing import Any

from .results import Port


def signature(binding: Any) -> tuple[Any, ...]:
    surface = binding.shrinkwrap.surface if binding.shrinkwrap else None
    return binding.id, binding.control, binding.kind, binding.target, binding.enabled, surface


def sources(binding: Any) -> tuple[str, ...]:
    if binding.shrinkwrap:
        return (binding.shrinkwrap.surface.target,)
    return (binding.control,) if binding.control else ()


def inputs(binding: Any) -> set[Port]:
    from .anatomical_surfaces import port

    if not binding.enabled:
        return set()
    if binding.shrinkwrap:
        surface = binding.shrinkwrap.surface
        return {port(surface), Port(surface.target, "pose")}
    return {Port(binding.control, "cage" if binding.kind == "LATTICE" else "control")}


def remapped(binding: Any, mapping: dict[str, str]) -> Any:
    from dataclasses import replace

    if not binding.shrinkwrap:
        return None
    ref = binding.shrinkwrap.surface
    return replace(
        binding.shrinkwrap, surface=replace(ref, target=mapping.get(ref.target, ref.target))
    )
