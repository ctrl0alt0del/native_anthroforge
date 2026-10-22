"""Semantic candidate installation; numeric addressing never bypasses object policies."""

from dataclasses import replace
from typing import Any

from anthroforge.core import numeric_properties as numeric
from anthroforge.core.construction import Control, Curve
from anthroforge.core.entities import SCP
from anthroforge.core.surfaces import Surface
from anthroforge.core.tissues import TissueVCP

from . import control_operations, object_operations, primitive_operations, tissue_operations
from .construction_policy import require_topology_edit


def editable(session: Any, target: str) -> Any:
    item = session.document.object(target)
    if isinstance(item, SCP):
        return session.editable(target)
    if isinstance(item, Control):
        return control_operations.editable(session, target)
    from .curve_edit_state import current

    return current(session, object_operations.editable(session, target))


def prepare(session: Any, target: str, updates: Any) -> tuple[Any, Any]:
    before = editable(session, target)
    after = numeric.batch(before, updates)
    validate(session, before, after)
    return before, after


def validate(session: Any, before: Any, after: Any) -> None:
    if isinstance(before, TissueVCP):
        from anthroforge.core.tissue_policy import validate as tissue_validate

        tissue_validate(after, session.document.registry.records)
        tissue_operations.require_inflation_topology(session, before, after)
    if topology_changed(before, after):
        require_topology_edit(session.document, before.id)


def topology_changed(before: Any, after: Any) -> bool:
    if isinstance(before, Curve):
        return any(
            getattr(before.engine_settings, n, None) != getattr(after.engine_settings, n, None)
            for n in ("resolution", "samples")
        )
    if isinstance(before, (TissueVCP, Control)):
        return bool(before.resolution != after.resolution)
    if isinstance(before, Surface):
        return (before.strips, before.patch_resolution) != (after.strips, after.patch_resolution)
    return False


def install(session: Any, before: Any, after: Any) -> None:
    if before == after:
        return
    if isinstance(after, SCP):
        install_scp(session, before, after)
    elif isinstance(after, Control):
        control_operations.install(session, after)
    else:
        object_operations.install(session, after)


def install_scp(session: Any, before: SCP, after: SCP) -> None:
    from . import construction_tasks, curve_sources, geometry_modifiers

    geometry_modifiers.validate_change(session.document, before, after.deformers)
    if before.primitive != after.primitive:
        primitive_operations.install(
            session, before.id, curve_sources.resolve(session.engine, session.document, after)
        )
        after = replace(after, primitive=session.document.entity(before.id).primitive)
    session.replace_entities({after.id: after})
    construction_tasks.edited(session, {after.id})
