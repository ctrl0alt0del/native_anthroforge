"""One deletion impact query for menu, keyboard, tree and inspector clients."""

from typing import Any

from anthroforge.core.construction import Control
from anthroforge.core.entities import SCP

from . import control_operations, dependencies, object_operations, object_removal


def inspect(session: Any, target: str) -> dict[str, Any]:
    item = session.document.registry.records[target]
    operation, arguments = command(item)
    validate(session, item)
    records = session.document.registry.records
    graph = dependencies.graph(session.document)
    seeds = {port for port in graph if port.owner == target}
    seeds.update(p for inputs in graph.values() for p in inputs if p.owner == target)
    affected = {p.owner for p in dependencies.closure(dependencies.reverse(graph), seeds)}
    affected.update(o.id for o in records.values() if related(o, target))
    affected.discard(target)
    rows = [dict(id=key, name=records[key].name) for key in sorted(affected) if key in records]
    return dict(operation=operation, arguments=arguments, affected=rows, name=item.name)


def related(item: Any, target: str) -> bool:
    return (
        getattr(item, "parent", "") == target
        or getattr(item, "follow", "") == target
        or target in getattr(item, "owners", ())
    )


def command(item: Any) -> tuple[str, dict[str, str]]:
    if isinstance(item, SCP):
        return "scp.delete", dict(entity=item.id)
    if isinstance(item, Control):
        return "control.delete", dict(control=item.id)
    return "object.delete", dict(target=item.id)


def validate(session: Any, item: Any) -> None:
    if isinstance(item, SCP):
        session.editable(item.id)
    elif isinstance(item, Control):
        control_operations.editable(session, item.id)
    else:
        object_operations.editable(session, item.id)
        object_removal.require_removable(session, item)
    object_removal.require_unbound(session, item.id)
