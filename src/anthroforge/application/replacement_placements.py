"""Explicit surface corrections use existing native current-shape editing and capture."""

from typing import Any

from anthroforge.native import curve_editing, path_editing

from .fiber_edit_evaluation import EditGeometry


def curve(engine: Any, current: Any, geometry: Any, goals: Any, cancel: int) -> Any:
    if not goals:
        return current, geometry
    indices = {point.id: index for index, point in enumerate(current.points)}
    if set(goals) - {binding.point for binding in current.bindings}:
        raise ValueError("Surface corrections must identify existing bound Fiber points.")
    edited = curve_editing.place(
        engine, current, [indices[k] for k in goals], list(goals.values()), geometry.world, cancel
    )
    path, records = path_editing.rebase(geometry.path, current, edited, cancel)
    return edited, EditGeometry(path, records, geometry.world)
