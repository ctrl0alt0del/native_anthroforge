"""Feature-owned command descriptions; execution policy is independent of routing."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from operator import attrgetter
from types import MappingProxyType
from typing import Any, Literal

Handler = Callable[..., Any]


@dataclass(frozen=True)
class Policy:
    mirror_guard: bool = False
    variant_guard: bool = False
    isolated: bool = False
    transaction: bool = False
    journal: Literal["none", "edit", "direct"] = "none"
    project_scope: bool = False


@dataclass(frozen=True)
class Command:
    name: str
    handler: Handler
    kind: Literal["edit", "query", "direct"]
    policy: Policy
    profiled: bool = True


def edit(
    name: str, handler: Handler, *, isolated: bool = False, project_scope: bool = False
) -> Command:
    return Command(name, handler, "edit", Policy(True, True, isolated, True, "edit", project_scope))


def query(name: str, handler: Handler) -> Command:
    return Command(name, handler, "query", Policy())


def direct(name: str, handler: Handler, *, journal: bool = True, profiled: bool = True) -> Command:
    """The handler owns its domain transaction, if any; never nest one implicitly."""
    return Command(
        name, handler, "direct", Policy(journal="direct" if journal else "none"), profiled
    )


def method(path: str) -> Handler:
    """Resolve a typed service's method at dispatch, never bind a superseded context."""
    resolve = attrgetter(path)

    def invoke(session: Any, **arguments: Any) -> Any:
        return resolve(session)(**arguments)

    return invoke


def catalogue(groups: Iterable[Iterable[Command]]) -> Mapping[str, Command]:
    result: dict[str, Command] = {}
    for group in groups:
        for command in group:
            if command.name in result:
                raise ValueError("Duplicate command declaration: " + command.name)
            result[command.name] = command
    return MappingProxyType(result)
