"""Explicit project-local anatomical types, instances and human review collections."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.reconstruction import AnatomicalAssignment, AnatomicalType, ReviewCollection

from . import reconstruction_state as records
from .operations import require_name

SIDES = {"UNSPECIFIED", "LEFT", "RIGHT", "MIDLINE"}


def create_type(
    session: Any, name: str, category: str = "OTHER", aliases: Any = (), description: str = ""
) -> str:
    row = AnatomicalType(require_name(name), require_name(category), tuple(aliases), description)
    return str(records.upsert(session, "types", row))


def update_type(session: Any, type_id: str, changes: Any) -> None:
    if set(changes) - {"name", "category", "aliases", "description"}:
        raise ValueError("Unknown anatomical type setting.")
    row = records.selected(session, "types", type_id)
    updated = replace(row, **changes)
    require_name(updated.name)
    records.upsert(session, "types", replace(updated, aliases=tuple(updated.aliases)))


def remove_type(session: Any, type_id: str) -> None:
    value = records.state(session)
    if any(row.type_id == type_id for row in (*value.assignments, *value.work)):
        raise ValueError("Remove type assignments and queue links before deleting this type.")
    records.remove(session, "types", type_id)


def assign(
    session: Any,
    target: str,
    type_id: str = "",
    side: str = "UNSPECIFIED",
    label: str = "",
    variant: str = "",
) -> None:
    records.subject(session, target, variant)
    if side not in SIDES:
        raise ValueError("Side must be Left, Right, Midline or Unspecified.")
    rows = tuple(r for r in records.state(session).assignments if r.target != target)
    rows += assignment(session, target, type_id, side, label) if type_id else ()
    records.install(session, assignments=rows)


def assignment(session: Any, target: str, type_id: str, side: str, label: str) -> Any:
    records.selected(session, "types", type_id)
    return (AnatomicalAssignment(target, type_id, side, label),)


def assign_many(session: Any, targets: list[str], **options: Any) -> None:
    type_id, side = options.get("type_id", ""), options.get("side", "UNSPECIFIED")
    validate_assignment_targets(session, targets, side, options.get("variant", ""))
    if type_id:
        records.selected(session, "types", type_id)
    rows = tuple(r for r in records.state(session).assignments if r.target not in targets)
    added = tuple(AnatomicalAssignment(k, type_id, side) for k in dict.fromkeys(targets))
    records.install(session, assignments=rows + (added if type_id else ()))


def validate_assignment_targets(session: Any, targets: Any, side: str, variant: str) -> None:
    if side not in SIDES:
        raise ValueError("Invalid instance side.")
    for key in targets:
        records.subject(session, key, variant)


def collection(session: Any, name: str, members: Any = (), collection: str = "") -> str:
    require_members(session, members)
    row = collection_row(session, name, collection)
    row = replace(row, name=require_name(name), members=tuple(dict.fromkeys(members)))
    return str(records.upsert(session, "collections", row))


def require_members(session: Any, members: Any) -> None:
    value = records.state(session)
    known = set(session.contexts.scene("").registry.anatomy) | {r.id for r in value.regions}
    known |= {k for v in value.variants for k in value.snapshot(v.current).registry.anatomy}
    if set(members) - known:
        raise ValueError("A collection member is not an anatomical instance or region.")


def collection_row(session: Any, name: str, collection: str) -> Any:
    return (
        records.selected(session, "collections", collection)
        if collection
        else ReviewCollection(name)
    )


def inspect(session: Any) -> dict[str, Any]:
    value = records.state(session)
    groups = ("types", "assignments", "collections", "regions")
    return {key: [asdict(row) for row in getattr(value, key)] for key in groups}


def execute(session: Any, operation: str, arguments: Any) -> Any:
    commands = operations()
    name = operation.removeprefix("catalogue.")
    if name in ("collection.remove", "region.remove"):
        return records.remove(session, name.split(".")[0] + "s", arguments["id"])
    if name not in commands:
        raise ValueError("Unknown catalogue operation.")
    return commands[name](session, **arguments)


def operations() -> dict[str, Any]:
    from . import reconstruction_regions

    return {
        "inspect": inspect,
        "type.create": create_type,
        "type.update": update_type,
        "type.remove": remove_type,
        "assign": assign,
        "assign_many": assign_many,
        "collection.set": collection,
        "region.set": reconstruction_regions.set_region,
        "region.inspect": reconstruction_regions.inspect,
    }
