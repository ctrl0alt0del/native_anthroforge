"""Explicit context-owned application state; resources and the worker pool remain shared."""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, cast

T = TypeVar("T")


@dataclass
class EditingState:
    key: str = ""
    values: dict[str, Any] = field(default_factory=dict)


# Nuitka's packaged PEP-695 scope loses T when used by runtime cast().
class ContextField(Generic[T]):  # noqa: UP046
    def __init__(self, name: str) -> None:
        self.name = name

    def __get__(self, instance: Any, owner: Any = None) -> T:
        if instance is None:
            return cast(T, self)
        if self.name not in instance._editing.values:
            raise AttributeError(self.name)
        return cast(T, instance._editing.values[self.name])

    def __set__(self, instance: Any, value: T) -> None:
        instance._editing.values[self.name] = value
