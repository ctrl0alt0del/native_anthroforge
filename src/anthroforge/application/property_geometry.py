"""Numerical edits retain the native handle and cage-resizing semantics of editor tools."""

from typing import Any

from anthroforge.core import numeric_properties as numeric
from anthroforge.core.construction import Control, Curve


def changed(session: Any, before: Any, updates: Any) -> Any:
    if isinstance(before, Control):
        return control(session, before, updates)
    after = numeric.batch(before, updates) if updates else before
    if isinstance(before, Curve) and before.points != after.points:
        from anthroforge.core.curve_shapes import reshaped

        points = tuple(point(session, before, index, p) for index, p in enumerate(after.points))
        return reshaped(after, points=points)
    return after


def point(session: Any, curve: Curve, index: int, changed: Any) -> Any:
    from anthroforge.native.curve_editing import FIELDS
    from anthroforge.native.curve_editing import point as edit_point

    before = curve.points[index]
    options = {
        name: getattr(changed, name)
        for name in FIELDS
        if getattr(before, name) != getattr(changed, name)
    }
    return edit_point(session.engine, curve, index, options) if options else changed


def control(session: Any, before: Control, updates: Any) -> Control:
    from .control_operations import resize_candidate

    resolutions = tuple(v for v in updates if v[0].path == ("resolution",))
    remainder = tuple(v for v in updates if v not in resolutions)
    if resolutions:
        dimensions = list(before.resolution)
        for reference, value in resolutions:
            if reference.component is None:
                dimensions = list(value)
            else:
                dimensions[reference.component] = value
        before = resize_candidate(session, before, dimensions)
    return numeric.batch(before, remainder) if remainder else before
