"""Current editable component read model shared by desktop and headless clients."""

from typing import Any

from anthroforge.core.component_reads import ComponentRead, component_key
from anthroforge.core.construction import Control, Curve
from anthroforge.core.entities import SCP
from anthroforge.core.tissues import TissueVCP

from . import component_buffers as buffers
from . import component_restrictions, component_tissue, curve_edit_state, curve_sources, query_pages
from .choice_queries import revision
from .construction_policy import topology_locks
from .query_projection import plain

CATEGORIES = frozenset(("CURVE", "BASE", "VERTEX", "CONTROL", "TISSUE_CONTROL", "TISSUE_FIELD"))
MEMBERSHIP = frozenset(("vertex", "base", "field"))


def current(session: Any, target: Any, category: Any = "CURVE", context: Any = None) -> Any:
    if category not in CATEGORIES:
        raise ValueError("Unknown editing category: " + category)
    context = dict(context or {})
    key = query_key(session, target, category, context)
    cached = session._editing.values.get("component_read")
    if cached and cached[0] is session.document and cached[1] == key:
        return cached[2]
    value = capture(session, target, category, context)
    session._editing.values["component_read"] = (session.document, key, value)
    return value


def query_key(session: Any, target: str, category: str, context: Any) -> Any:
    return target, category, tuple(sorted(context.items())), session.workspace, session.waiting_save


def capture(session: Any, target: Any, category: Any, context: Any) -> Any:
    item = session.document.object(target)
    resolved = (
        curve_sources.for_editing(session, item)
        if isinstance(item, SCP)
        else curve_edit_state.current(session, item)
    )
    records = groups(session, resolved, category, context)
    return ComponentRead(
        signature(session, target, category, context),
        records,
        tuple(provenance(item, resolved).items()),
        edit_reason(session, item),
        component_restrictions.weight_binding(session, item, context),
    )


def signature(session: Any, target: str, category: str, context: Any) -> str:
    key = (
        str(session.document.id),
        id(session.document),
        query_key(session, target, category, context),
    )
    return revision(session, key)


def groups(session: Any, item: Any, category: Any, context: Any) -> Any:
    if isinstance(item, Control):
        return (buffers.control(session, item),)
    if isinstance(item, Curve):
        return (buffers.curve(session, item, item),)
    if isinstance(item, TissueVCP):
        if category == "TISSUE_FIELD":
            return component_tissue.fields(session, item, context)
        return (
            component_tissue.controls(session, item, context)
            if category == "TISSUE_CONTROL"
            else ()
        )
    return primitive_groups(session, item, category)


def primitive_groups(session: Any, item: Any, category: Any) -> Any:
    if not isinstance(item, SCP) or not item.primitive:
        return ()
    if item.primitive.kind == "BODY" and category == "BASE":
        return tuple(buffers.base(session, item, p) for p in item.primitive.pieces)
    if item.primitive.kind == "IMPORTED":
        return (buffers.imported(session, item),)
    return tuple(buffers.curve(session, item, curve) for curve in item.primitive.curves)


def edit_reason(session: Any, item: Any) -> Any:
    from . import control_operations, object_operations

    try:
        if isinstance(item, SCP):
            session.editable(item.id)
        elif isinstance(item, Control):
            control_operations.editable(session, item.id)
        else:
            object_operations.editable(session, item.id)
    except ValueError as error:
        return str(error)
    return ""


def provenance(item: Any, resolved: Any) -> Any:
    result = getattr(item, "result", None)
    return dict(
        authored_revision=item.generation,
        accepted_revision=getattr(result, "revision", 0),
        pending=getattr(result, "pending", ()),
        status=getattr(result, "status", ""),
        input_revisions=getattr(result, "inputs", ()),
        source="RESOLVED" if resolved is not item else "AUTHORED",
        active_edit=getattr(item, "edit", None) is not None,
    )


def rows(value: Any) -> Any:
    return [
        (group.reference(i), group.world[i].tolist(), list(group.local[i]))
        for group in value.buffers
        for i in range(len(group.local))
    ]


def inspect(
    session: Any,
    target: Any,
    category: Any = "CURVE",
    context: Any = None,
    offset: Any = 0,
    limit: Any = 4096,
    expected_revision: Any = None,
) -> Any:
    start, end = query_pages.bounds(offset, limit)
    value = current(session, target, category, context)
    query_pages.require_revision(expected_revision, value.signature)
    return report(session, target, category, value, start, end)


def report(
    session: Any, target: str, category: str, value: ComponentRead, start: int, end: int
) -> Any:
    total = sum(len(group.local) for group in value.buffers)
    return dict(
        target=target,
        category=category,
        revision=value.signature,
        total=total,
        offset=start,
        next_offset=end if end < total else None,
        components=page(value, start, end),
        provenance=plain(dict(value.provenance)),
        topology_locks=topology_locks(session.document, target),
    )


def page(value: Any, start: Any, end: Any) -> Any:
    result: list[Any] = []
    preceding = 0
    for group in value.buffers:
        result.extend(
            component(group, i, value.reason, value.weight_binding)
            for i in range(max(0, start - preceding), min(len(group.local), end - preceding))
        )
        preceding += len(group.local)
    return result


def component(group: Any, index: Any, reason: Any, binding: Any = None) -> Any:
    ref = group.reference(index)
    position_reason = position_restriction(ref, reason)
    return dict(
        key=component_key(ref),
        reference=ref,
        local=list(group.local[index]),
        world=group.world[index].tolist(),
        frame=group.frame,
        position_editable=not position_reason,
        position_reason=position_reason,
        **component_restrictions.weights(ref, binding, reason),
    )


def position_restriction(ref: Any, reason: str) -> str:
    if ref["part"] in MEMBERSHIP:
        return reason or "Membership/field point; position editing is unavailable."
    return reason or ref.get("reason", "")
