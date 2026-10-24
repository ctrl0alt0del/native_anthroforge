"""Surface authoring uses shared curves, validation and asynchronous layout transactions."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.fibers import Fiber
from anthroforge.core.membranes import Membrane
from anthroforge.core.mirroring import SymmetricHalf
from anthroforge.core.object_registry import validate_sources
from anthroforge.core.surfaces import Surface

from . import (
    authored_jobs,
    curve_consumers,
    object_creation,
    object_operations,
    surface_grouping,
    surface_jobs,
)
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
    item = definition(session, curves, kind, name, parent, owner, options)
    return authored_jobs.begin(session, partial(surface_jobs.enqueue, session, item, False))


def definition(
    session: Any, curves: Any, kind: str, name: str, parent: str, owner: str, options: Any
) -> Surface:
    grouping = options.pop("grouping", None)
    if kind == "AUTO":
        kind, grouping = automatic(session, curves, grouping)
    item = new_surface(
        session, curves, kind, name, parent, owner, options.get("mirrored_rows", False)
    )
    item = grouped(session, item, curves, grouping)
    item = configured(item, options)
    validate_sources(item, session.document.registry.records)
    return item


def grouped(session: Any, item: Surface, curves: Any, grouping: Any) -> Surface:
    if grouping is None:
        return item
    records = session.document.registry.records
    result: Surface = surface_grouping.apply(
        item, surface_grouping.checked(records, curves, grouping), records
    )
    return result


def automatic(session: Any, curves: list[str], grouping: Any) -> tuple[str, Any]:
    if len(curves) == 1:
        return "PATCH", None
    if grouping is not None:
        return "LOFT", grouping
    result = surface_grouping.infer(session, curves)
    if result["ambiguous"]:
        raise ValueError(
            "Ambiguous branch groups: inspect surface.grouping and provide grouping explicitly."
        )
    return "LOFT", result["plan"]


def new_surface(
    session: Any,
    curves: list[str],
    kind: str,
    name: str,
    parent: str,
    owner: str,
    mirrored_rows: bool = False,
) -> Surface:
    placement = object_creation.placement(session, parent, owner, None)
    item = surface_record(session, curves, kind, name, placement, mirrored_rows)
    uses = tuple(curve_consumers.bind(session, item, key) for key in curves)
    return replace(item, curves=uses)


def surface_record(
    session: Any, curves: Any, kind: str, name: str, placement: Any, mirrored: bool
) -> Surface:
    surface_type = (
        Membrane if all(isinstance(session.document.object(k), Fiber) for k in curves) else Surface
    )
    item = surface_type(
        name=require_name(name),
        kind=kind,
        curves=tuple(CurveUse(key) for key in curves),
        mirrored_rows=mirrored,
        **placement,
    )
    return item


def editable(session: Any, target: str) -> Surface:
    item = object_operations.editable(session, target)
    if not isinstance(item, Surface):
        raise ValueError("Select a curve surface.")
    return item


def configured(item: Surface, values: dict[str, Any]) -> Surface:
    allowed = {"name", "exact", "strips", "patch_resolution", "close_across", "flip"}
    if set(values) - allowed - {"mirrored_rows", "mirror_plane"}:
        raise ValueError("Unknown surface setting.")
    if isinstance(values.get("mirror_plane"), dict):
        values = dict(values, mirror_plane=SymmetricHalf(**values["mirror_plane"]))
    if "mirrored_rows" in values and values["mirrored_rows"] != item.mirrored_rows:
        values = dict(values, mirror_order=(), across=())
    changed = replace(item, **values)
    if "strips" in values and changed.strips:
        count = len(changed.mirror_order) if changed.mirror_order else len(changed.curves)
        changed = replace(changed, across=(changed.strips - 1,) * (count - 1))
    return changed


def update(session: Any, target: str, **options: Any) -> None:
    item = editable(session, target)
    candidate = configured(item, options)
    if candidate.mirrored_rows != item.mirrored_rows:
        return configure_mirroring(session, candidate)
    object_operations.install(session, candidate)


def configure_mirroring(session: Any, candidate: Surface) -> None:
    from .construction_policy import require_topology_edit

    require_topology_edit(session.document, candidate.id)
    authored_jobs.begin(session, partial(surface_jobs.enqueue, session, candidate, True))


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
    from .surface_sources import assign

    item = editable(session, target)
    if item.branches:
        raise ValueError("Remove branches before changing the main source order.")
    if len(curves) != len(item.curves) or set(curves) != {u.curve for u in item.curves}:
        raise ValueError("Reordering requires every surface source exactly once.")
    assign(session, target, curves)
