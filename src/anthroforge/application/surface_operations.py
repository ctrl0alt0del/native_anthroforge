"""Surface authoring uses shared curves, validation and asynchronous layout transactions."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.object_registry import validate_sources
from anthroforge.core.surfaces import Surface

from . import authored_jobs, curve_consumers, object_creation, object_operations, surface_jobs
from .operations import require_name


def create(
    session: Any,
    curves: list[str],
    kind: str = "LOFT",
    name: str = "Surface",
    parent: str = "",
    owner: str = "",
    **options: Any,
) -> str:
    item = new_surface(session, curves, kind, name, parent, owner)
    item = configured(item, options)
    validate_sources(item, session.document.registry.records)
    return authored_jobs.begin(session, partial(surface_jobs.enqueue, session, item, False))


def new_surface(
    session: Any, curves: list[str], kind: str, name: str, parent: str, owner: str
) -> Surface:
    placement = object_creation.placement(session, parent, owner, None)
    surface_type = (
        Membrane if all(isinstance(session.document.object(k), Fiber) for k in curves) else Surface
    )
    item = surface_type(
        name=require_name(name),
        kind=kind,
        curves=tuple(CurveUse(key) for key in curves),
        **placement,
    )
    uses = tuple(curve_consumers.bind(session, item, key) for key in curves)
    return replace(item, curves=uses)


def editable(session: Any, target: str) -> Surface:
    item = object_operations.editable(session, target)
    if not isinstance(item, Surface):
        raise ValueError("Select a curve surface.")
    return item


def configured(item: Surface, values: dict[str, Any]) -> Surface:
    if set(values) - {"name", "exact", "strips", "patch_resolution", "close_across", "flip"}:
        raise ValueError("Unknown surface setting.")
    changed = replace(item, **values)
    if "strips" in values and changed.strips:
        changed = replace(changed, across=(changed.strips - 1,) * (len(changed.curves) - 1))
    return changed


def update(session: Any, target: str, **options: Any) -> None:
    object_operations.install(session, configured(editable(session, target), options))


def realign(session: Any, target: str) -> str:
    item = editable(session, target)
    return authored_jobs.begin(session, partial(surface_jobs.enqueue, session, item, True))


def source(session: Any, target: str, curve: str, **values: Any) -> None:
    item = editable(session, target)
    use = next((u for u in item.curves if u.curve == curve), None)
    if use is None or set(values) - {"mode", "reverse", "start", "span", "samples"}:
        raise ValueError("Select a surface source and supported consumption settings.")
    if "mode" in values:
        use = curve_consumers.rebound_use(session, use, values.pop("mode"))
    changed = replace(use, **values)
    object_operations.install(
        session,
        replace(item, curves=tuple(changed if u.curve == curve else u for u in item.curves)),
    )


def order(session: Any, target: str, curves: list[str]) -> None:
    from .surface_sources import configured as configure_sources

    item = editable(session, target)
    if item.branches:
        raise ValueError("Remove branches before changing the main source order.")
    if len(curves) != len(item.curves) or set(curves) != {u.curve for u in item.curves}:
        raise ValueError("Reordering requires every surface source exactly once.")
    object_operations.install(session, configure_sources(session, item, curves))
