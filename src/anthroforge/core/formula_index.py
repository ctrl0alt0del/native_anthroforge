"""Snapshot-owned formula lookup; shared across geometry-only publications."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from .shortcuts import DrivingFormula, DrivingShortcut, FormulaResult


@dataclass(frozen=True, slots=True)
class FormulaIndex:
    source: tuple[DrivingShortcut, ...]
    accepted: tuple[FormulaResult, ...]
    drivers: Mapping[str, DrivingShortcut]
    formulas: Mapping[str, tuple[DrivingShortcut, DrivingFormula]]
    results: Mapping[str, FormulaResult]


def build(
    drivers: tuple[DrivingShortcut, ...],
    results: tuple[FormulaResult, ...],
    previous: FormulaIndex | None,
) -> FormulaIndex:
    if previous and drivers is previous.source and results is previous.accepted:
        return previous
    authored, formulas = definitions(drivers, previous)
    accepted = (
        previous.results
        if previous and results is previous.accepted
        else MappingProxyType({r.formula: r for r in results})
    )
    return FormulaIndex(drivers, results, authored, formulas, accepted)


def definitions(
    drivers: tuple[DrivingShortcut, ...], previous: FormulaIndex | None
) -> tuple[Mapping[str, DrivingShortcut], Mapping[str, tuple[DrivingShortcut, DrivingFormula]]]:
    if previous and drivers is previous.source:
        return previous.drivers, previous.formulas
    return MappingProxyType({d.id: d for d in drivers}), MappingProxyType(
        {f.id: (d, f) for d in drivers for f in d.formulas if f.enabled}
    )
