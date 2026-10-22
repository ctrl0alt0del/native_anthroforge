"""Stable numerical addresses; properties carry no shortcut edit policies."""

from dataclasses import dataclass, replace
from math import isfinite
from numbers import Integral, Real
from typing import Any


@dataclass(frozen=True, slots=True)
class PropertyRef:
    target: str
    path: tuple[str, ...]
    component: int | None = None

    def __post_init__(self) -> None:
        if not self.target or not self.path or any(not p or p.startswith("_") for p in self.path):
            raise ValueError("A numerical property requires a target and public stable path.")
        if self.component is not None and (type(self.component) is not int or self.component < 0):
            raise ValueError("A property component must be a nonnegative integer.")


@dataclass(frozen=True, slots=True)
class NumericDescriptor:
    reference: PropertyRef
    label: str
    numeric_type: str
    dimension: str = "SCALAR"
    components: int = 1
    writable: bool = True
    reason: str = ""

    def validate(self, value: Any) -> int | float | tuple[int | float, ...]:
        values = tuple(value) if isinstance(value, (list, tuple)) else (value,)
        count = 1 if self.reference.component is not None else self.components
        if len(values) != count:
            raise ValueError(f"{self.label} requires {count} numerical components.")
        for item in values:
            validate_number(item, self.numeric_type)
        return values if count > 1 else values[0]


def validate_number(value: Any, kind: str) -> None:
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError("A numerical value must be finite; Boolean is not a number.")
    if kind == "INTEGER" and type(value) is not int:
        raise ValueError("Integer properties require integer results; use round, floor or ceil.")


def decode_reference(value: PropertyRef | dict[str, Any]) -> PropertyRef:
    if isinstance(value, PropertyRef):
        return value
    return PropertyRef(value["target"], tuple(value["path"]), value.get("component"))


def member(value: Any, token: str) -> Any:
    if isinstance(value, tuple):
        if token.startswith("#") and token[1:].isdigit() and int(token[1:]) < len(value):
            return value[int(token[1:])]
        matches = [v for v in value if member_identity(v) == token.removeprefix("@")]
        if not token.startswith("@") or len(matches) != 1:
            raise ValueError("Collection properties require an existing stable member identity.")
        return matches[0]
    if token.startswith("_") or not hasattr(value, token):
        raise ValueError(f"Unknown numerical property member: {token}")
    return getattr(value, token)


def member_identity(value: Any) -> str | None:
    return getattr(value, "id", None) or getattr(value, "name", None)


def member_token(value: Any, index: int) -> str:
    identity = member_identity(value)
    return "@" + identity if identity else "#" + str(index)


def read_path(value: Any, path: tuple[str, ...]) -> Any:
    for token in path:
        value = member(value, token)
    return value


def replace_path(value: Any, path: tuple[str, ...], replacement: Any) -> Any:
    if not path:
        return replacement
    child = member(value, path[0])
    updated = replace_path(child, path[1:], replacement)
    if isinstance(value, tuple):
        return tuple(updated if member_token(v, i) == path[0] else v for i, v in enumerate(value))
    return replace(value, **{path[0]: updated})


def read(value: Any, reference: PropertyRef) -> Any:
    result = read_path(value, reference.path)
    if reference.component is None:
        return tuple(scalar(v) for v in result) if isinstance(result, tuple) else scalar(result)
    if not isinstance(result, tuple) or reference.component >= len(result):
        raise ValueError("Numerical property component is unavailable.")
    return scalar(result[reference.component])


def scalar(value: Any) -> Any:
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    return float(value) if isinstance(value, Real) and not isinstance(value, bool) else value


def changed(value: Any, reference: PropertyRef, replacement: Any) -> Any:
    if reference.component is not None:
        previous = read_path(value, reference.path)
        replacement = tuple(
            replacement if index == reference.component else v for index, v in enumerate(previous)
        )
    return replace_path(value, reference.path, replacement)


def overlaps(first: PropertyRef, second: PropertyRef) -> bool:
    return (
        first.target == second.target
        and first.path == second.path
        and (
            first.component is None
            or second.component is None
            or first.component == second.component
        )
    )


def batch(value: Any, updates: tuple[tuple[PropertyRef, Any], ...]) -> Any:
    paths: dict[tuple[str, ...], Any] = {}
    for reference, replacement in updates:
        if reference.component is not None:
            current = paths.get(reference.path, read_path(value, reference.path))
            replacement = tuple(
                replacement if i == reference.component else v for i, v in enumerate(current)
            )
        paths[reference.path] = replacement
    return rebuild(value, paths)


def rebuild(value: Any, paths: dict[tuple[str, ...], Any]) -> Any:
    if () in paths:
        return paths[()]
    groups: dict[str, dict[tuple[str, ...], Any]] = {}
    for path, replacement in paths.items():
        groups.setdefault(path[0], {})[path[1:]] = replacement
    changed = {token: rebuild(member(value, token), items) for token, items in groups.items()}
    if isinstance(value, tuple):
        return tuple(changed.get(member_token(v, i), v) for i, v in enumerate(value))
    return replace(value, **changed)
