"""Accepted evaluation provenance; never an editable construction."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Port:
    owner: str
    output: str


@dataclass(frozen=True, slots=True)
class ReadRevision:
    owner: str
    output: str
    authored: int
    accepted: int
    membership: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    asset: str = ""
    revision: int = 0
    authored_revision: int = 0
    inputs: tuple[ReadRevision, ...] = ()
    pending: tuple[str, ...] = ()
    status: str = "ready"
    error: str = ""


@dataclass(frozen=True, slots=True)
class ControlResult:
    matrix: tuple[float, ...] = ()
    inputs: tuple[ReadRevision, ...] = ()
    revision: int = 0
    status: str = "ready"
    error: str = ""


def geometry_asset(entity: object) -> str:
    result = getattr(entity, "result", None)
    accepted = getattr(result, "asset", "")
    return str(accepted or getattr(entity, "asset", ""))
