"""Typed graph traversal; ordinary text and numerical arrays are never identity-rewritten."""

from dataclasses import dataclass, fields, is_dataclass, replace
from typing import Any

from .graph_contracts import Field, schema
from .mirroring import MirrorInstance, parse


@dataclass(frozen=True)
class Reference:
    target: str
    relationship: str
    required: bool
    path: tuple[str | int, ...]
    output: str = ""
    role: str = ""
    instance: str = ""


def walk(value: Any, path: tuple[str | int, ...] = ()) -> Any:
    if isinstance(value, tuple) and value and is_dataclass(value[0]):
        for index, item in enumerate(value):
            yield from walk(item, (*path, index))
    elif is_dataclass(value) and not isinstance(value, type):
        yield value, path
        for field in fields(value):
            yield from walk(getattr(value, field.name), (*path, field.name))


def owned(value: Any) -> set[str]:
    return {
        getattr(item, name)
        for item, _ in walk(value)
        for name, rule in schema(item).items()
        if rule.mode == "id" and getattr(item, name)
    }


def references(value: Any) -> tuple[Reference, ...]:
    result = []
    for item, path in walk(value):
        for name, rule in schema(item).items():
            if rule.mode == "reference":
                result.extend(field_references(item, name, rule, path))
    return tuple(result)


def field_references(item: Any, name: str, rule: Field, path: Any) -> list[Reference]:
    value, role = getattr(item, name), getattr(item, "role", "")
    instance = getattr(item, "instance", "") if rule.relationship == "support" else ""
    values = enumerate(value) if isinstance(value, tuple) else ((None, value),)
    return [
        make_reference(key, rule, (*path, name, *(() if i is None else (i,))), role, instance)
        for i, key in values
        if key
    ]


def make_reference(target: str, rule: Field, path: Any, role: str, instance: str = "") -> Reference:
    return Reference(target, rule.relationship, rule.required, path, rule.output, role, instance)


def rewritten(
    value: Any, identities: dict[str, str], resources: dict[str, str] | None = None
) -> Any:
    if isinstance(value, tuple):
        return rewritten_tuple(value, identities, resources)
    if not is_dataclass(value) or isinstance(value, type):
        return value
    return replace(value, **rewritten_fields(value, identities, resources or {}))


def rewritten_tuple(value: tuple[Any, ...], ids: Any, resources: Any) -> Any:
    if not value or not is_dataclass(value[0]):
        return value
    return tuple(rewritten(v, ids, resources) for v in value)


def rewritten_fields(value: Any, identities: Any, resources: Any) -> dict[str, Any]:
    rules = schema(value)
    return {
        f.name: rewrite_field(getattr(value, f.name), rules.get(f.name), identities, resources)
        for f in fields(value)
        if f.init
    }


def rewrite_field(
    value: Any, rule: Field | None, ids: dict[str, str], assets: dict[str, str]
) -> Any:
    if rule is None:
        return rewritten(value, ids, assets)
    if rule.mode == "resource":
        return assets.get(value, value)
    if rule.mode in ("members", "weights", "pairs", "property_path", "port"):
        return encoded(value, rule.mode, ids)
    return tuple(key(v, ids) for v in value) if isinstance(value, tuple) else key(value, ids)


def key(value: str, ids: dict[str, str]) -> str:
    if value in ids:
        return ids[value]
    instance = parse(value)
    if instance:
        return MirrorInstance(
            ids.get(instance.source, instance.source), ids.get(instance.rule, instance.rule)
        ).id
    return value


def member(value: str, ids: dict[str, str]) -> str:
    point, component = value.rsplit(":", 1)
    return key(point, ids) + ":" + component


def encoded(value: Any, mode: str, ids: dict[str, str]) -> Any:
    if mode == "members":
        return tuple(member(v, ids) for v in value)
    if mode in ("weights", "pairs"):
        convert = member if mode == "weights" else key
        return tuple((convert(k, ids), v) for k, v in value)
    if mode == "property_path":
        return tuple("@" + key(v[1:], ids) if v.startswith("@") else v for v in value)
    if value.startswith("junction:"):
        return "junction:" + key(value.removeprefix("junction:"), ids)
    if value.startswith("property:"):
        return property_output(value, ids)
    return value


def property_output(value: str, ids: dict[str, str]) -> str:
    from .formula_dependencies import property_port, property_reference
    from .results import Port

    reference = property_reference(Port("owner", value))
    return property_port(rewritten(reference, ids)).output


def replace_at(value: Any, path: tuple[str | int, ...], changed: Any) -> Any:
    if not path:
        return changed
    first, *rest = path
    if isinstance(first, int):
        items = list(value)
        items[first] = replace_at(items[first], tuple(rest), changed)
        return tuple(items)
    return replace(value, **{first: replace_at(getattr(value, first), tuple(rest), changed)})
