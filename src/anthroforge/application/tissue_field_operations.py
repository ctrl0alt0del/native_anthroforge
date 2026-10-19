"""Topology-qualified field edits shared by desktop tools and headless authoring."""

from typing import Any

from anthroforge.native.tissue_shapes import field_edit

from . import tissue_fields, tissue_strategy_operations
from .tissue_operations import tissue


def create(session: Any, target: str, name: str, domain: str = "BASE", value: float = 0) -> None:
    item = tissue(session, target)
    if any(f.name == name for f in item.fields):
        raise ValueError("A field with this name already exists; edit or remove it explicitly.")
    count, _ = tissue_fields.domain(session.resources, item, domain)
    values = field_edit(session.engine, count, (), (), value)
    tissue_strategy_operations.field_set(session, target, name, values.tolist(), domain)


def assign(
    session: Any, target: str, name: str, indices: list[int], value: float, topology: str
) -> None:
    item = tissue(session, target)
    field = next((f for f in item.fields if f.name == name), None)
    if field is None:
        raise ValueError("Choose an existing tissue field.")
    count, signature = tissue_fields.domain(session.resources, item, field.domain)
    if signature != topology or signature != field.topology:
        raise ValueError("The material domain changed; explicitly replace the field and selection.")
    if not indices:
        raise ValueError("Select field points before assigning a weight.")
    values = field_edit(session.engine, count, field.values, indices, value)
    tissue_strategy_operations.field_set(session, target, name, values.tolist(), field.domain)
