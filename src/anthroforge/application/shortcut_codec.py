"""Portable shortcut definitions; no compiled expression handles enter documents."""

from typing import Any

from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.shortcuts import (
    AttachmentPolicy,
    DescendantOverride,
    DrivingFormula,
    DrivingShortcut,
    FormulaInput,
    FormulaResult,
    Shortcut,
)


def policy(value: dict[str, Any]) -> AttachmentPolicy:
    return AttachmentPolicy(
        value.get("backsolve", False),
        tuple(DescendantOverride(**v) for v in value.get("descendants", ())),
    )


def shortcut(value: dict[str, Any]) -> Shortcut:
    return Shortcut(
        decode_reference(value["reference"]),
        value.get("label", ""),
        value.get("exposed", False),
        policy(value.get("policy", {})),
    )


def formula_input(value: dict[str, Any]) -> FormulaInput:
    reference = decode_reference(value["property"]) if value.get("property") else None
    return FormulaInput(value["name"], reference, value.get("driver", ""))


def formula(value: dict[str, Any]) -> DrivingFormula:
    data = dict(value, target=decode_reference(value["target"]))
    data["inputs"] = tuple(formula_input(v) for v in value.get("inputs", ()))
    return DrivingFormula(**data)


def driver(value: dict[str, Any]) -> DrivingShortcut:
    data = dict(value, policy=policy(value.get("policy", {})))
    data["formulas"] = tuple(formula(v) for v in value.get("formulas", ()))
    return DrivingShortcut(**data)


def result(value: dict[str, Any]) -> FormulaResult:
    data = dict(value, inputs=tuple(tuple(v) for v in value.get("inputs", ())))
    if isinstance(data.get("value"), list):
        data["value"] = tuple(data["value"])
    return FormulaResult(**data)


def document_fields(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "shortcuts": tuple(shortcut(v) for v in value.get("shortcuts", ())),
        "driving_shortcuts": tuple(driver(v) for v in value.get("driving_shortcuts", ())),
        "formula_results": tuple(result(v) for v in value.get("formula_results", ())),
    }
