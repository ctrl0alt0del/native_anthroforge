"""Surface-driven deformation uses the common binding lifecycle and transactions."""

from dataclasses import replace
from typing import Any

from anthroforge.core.construction import Deformer, Target
from anthroforge.core.shrinkwrap import Shrinkwrap

from . import deformer_operations as bindings
from .surface_providers import normalize


def add(
    session: Any,
    target: dict[str, Any],
    surface: Any,
    offset: float = 0.0,
    mode: str = "ON_SURFACE",
) -> str:
    selected = Target(**target)
    bindings.validate_target(session, selected, "SHRINKWRAP")
    settings = Shrinkwrap(normalize(session.document, surface), offset, mode)
    binding = Deformer("SHRINKWRAP", "", selected, shrinkwrap=settings)
    bindings.install(session, selected, (*bindings.owner(session, selected).deformers, binding))
    return binding.id


def update(session: Any, binding: str, **options: Any) -> None:
    current = bindings.locate(session, binding)
    if current.shrinkwrap is None or set(options) - {"surface", "offset", "mode"}:
        raise ValueError("Choose a Shrinkwrap binding and valid settings.")
    if "surface" in options:
        options["surface"] = normalize(session.document, options["surface"])
    changed = replace(current, shrinkwrap=replace(current.shrinkwrap, **options))
    values = tuple(
        changed if b.id == binding else b for b in bindings.owner(session, current.target).deformers
    )
    bindings.install(session, current.target, values)
