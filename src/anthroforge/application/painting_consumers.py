"""Explicit field-painting adapters; the lifecycle is independent of effect storage."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from . import skin_painting, tissue_painting

ALIASES = {"paint": "tissue_weights", "collagen": "collagen", "tissue_weights": "tissue_weights"}


@dataclass(frozen=True)
class Consumer:
    kind: str
    validate: Callable[..., Any]
    signature: Callable[..., Any]
    compute: Callable[..., Any]
    workload: Callable[..., Any]
    apply: Callable[..., Any]
    require: Callable[..., Any]
    read: Callable[..., Any]


def name(kind: str) -> str:
    if kind not in ALIASES:
        raise ValueError("Unknown painting consumer: " + kind)
    return ALIASES[kind]


def consumer(kind: str) -> Consumer:
    return collagen() if name(kind) == "collagen" else tissue()


def collagen() -> Consumer:
    return Consumer(
        "collagen", skin_painting.validate, skin_painting.signature,
        skin_painting.compute, skin_painting.workload, apply_collagen,
        require_collagen, read_values,
    )


def tissue() -> Consumer:
    return Consumer(
        "paint", tissue_painting.validate, tissue_painting.signature,
        tissue_painting.compute, tissue_painting_workload, apply_tissue,
        require_tissue, read_values,
    )


def tissue_painting_workload(context: Any, target: str, options: Any) -> Any:
    from .tissue_inspection import workload

    return workload(context, target, options)


def require_tissue(session: Any, target: str) -> None:
    from .tissue_operations import tissue

    tissue(session, target)


def require_collagen(session: Any, target: str) -> None:
    session.editable(target)


def apply_tissue(session: Any, value: Any) -> None:
    from . import tissue_strategy_operations

    result = value.asset
    field = tissue_painting.field(session, value.target, value.options)
    weights = result["resource"].values.tolist()
    if tuple(weights) != field.values:
        tissue_strategy_operations.field_set(
            session, value.target, field.name, weights, field.domain
        )


def apply_collagen(session: Any, value: Any) -> None:
    from . import skin_collagen

    mesh = skin_collagen.mesh(session, value.target)
    baseline = skin_painting.baseline(session, value.target, mesh)
    weights = value.asset["resource"].values
    if (baseline != weights).any():
        skin_collagen.set_weights(session, value.target, weights)


def read_values(asset: Any, offset: int, limit: int) -> tuple[int, list[float]]:
    values = asset["resource"].values
    return len(values), values[offset : offset + limit].tolist()
