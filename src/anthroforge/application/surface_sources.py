"""Surface source-list changes preserve existing consumption and correspondence records."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surfaces import Surface, SurfaceAlignment

from . import curve_consumers, object_operations, surface_operations


def identities(session: Any, target: str) -> list[str]:
    item = session.document.object(target)
    if not isinstance(item, Surface):
        raise ValueError("Choose a surface or Membrane to inspect its sources.")
    return [use.curve for use in item.curves]


def assign(session: Any, target: str, curves: list[str]) -> None:
    item = surface_operations.editable(session, target)
    if item.branches:
        raise ValueError("Remove branches before replacing the main source list.")
    object_operations.install(session, configured(session, item, curves))


def configured(session: Any, item: Any, curves: list[str]) -> Any:
    previous = {u.curve: u for u in item.curves}
    alignment = dict(zip(previous, item.alignment, strict=False))
    uses = tuple(
        previous[key] if key in previous else curve_consumers.bind(session, item, key)
        for key in curves
    )
    return replace(
        item,
        curves=uses,
        alignment=tuple(alignment.get(key, SurfaceAlignment()) for key in curves),
        across=retained_counts(item, curves),
    )


def retained_counts(item: Any, curves: list[str]) -> tuple[int, ...]:
    if not item.across:
        return ()
    old = [use.curve for use in item.curves]
    pairs = (frozenset(pair) for pair in zip(old, old[1:], strict=False))
    counts = dict(zip(pairs, item.across, strict=True))
    default = max(1, item.strips) - 1
    return tuple(
        counts.get(frozenset(pair), default) for pair in zip(curves, curves[1:], strict=False)
    )


def add(session: Any, target: str, curve: str, index: int | None = None) -> None:
    item = surface_operations.editable(session, target)
    curves = [u.curve for u in item.curves]
    index = len(curves) if index is None else index
    if not isinstance(index, int) or not 0 <= index <= len(curves):
        raise ValueError("Choose a source insertion position within the list.")
    curves.insert(index, curve)
    assign(session, target, curves)


def remove(session: Any, target: str, curve: str) -> None:
    item = surface_operations.editable(session, target)
    if curve not in {u.curve for u in item.curves}:
        raise ValueError("Unknown surface source.")
    assign(session, target, [u.curve for u in item.curves if u.curve != curve])
