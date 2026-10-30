"""Context-owned lifecycle subscriptions; never a lookup mechanism for feature services."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class Event(Enum):
    DOCUMENT_CHANGED = auto()
    SYNCHRONIZE = auto()
    INTERACTION_CANCEL = auto()
    HISTORY_BEGIN = auto()
    HISTORY_RESTORED = auto()
    GESTURE_BEGIN = auto()
    GESTURE_COMMITTED = auto()
    GESTURE_CANCELING = auto()
    CLOSE = auto()


Callback = Callable[..., None]


@dataclass(frozen=True)
class Service:
    name: str
    hooks: tuple[tuple[Event, Callback], ...]


class Lifecycle:
    def __init__(self) -> None:
        self.names: set[str] = set()
        self.hooks: dict[Event, list[Callback]] = {}
        self.closed = False

    def register(self, service: Service) -> None:
        if self.closed or service.name in self.names:
            raise ValueError("Cannot register context service: " + service.name)
        self.names.add(service.name)
        for event, callback in service.hooks:
            self.hooks.setdefault(event, []).append(callback)

    def emit(self, event: Event, *arguments: Any) -> None:
        if not self.closed:
            for callback in tuple(self.hooks.get(event, ())):
                callback(*arguments)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        errors = []
        for callback in self.hooks.get(Event.CLOSE, ()):
            try:
                callback()
            except Exception as error:
                errors.append(error)
        self.hooks.clear()
        if errors:
            raise ExceptionGroup("Context service cleanup failed", errors)
