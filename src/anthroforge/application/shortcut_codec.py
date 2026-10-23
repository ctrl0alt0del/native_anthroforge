"""Portable shortcut definitions; no compiled expression handles enter documents."""

from typing import Any

from anthroforge.core.entities import Attachment
from anthroforge.core.numeric_properties import decode_reference
from anthroforge.core.results import ReadRevision
from anthroforge.core.shortcut_edits import OverrideBinding, OwnerAnchor, ShortcutEdit
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
    data = dict(
        value,
        inputs=tuple(
            ReadRevision(**dict(v, membership=tuple(v.get("membership", ()))))
            for v in value.get("inputs", ())
        ),
    )
    data["pending"] = tuple(value.get("pending", ()))
    if isinstance(data.get("value"), list):
        data["value"] = tuple(data["value"])
    return FormulaResult(**data)


def document_fields(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "shortcuts": tuple(shortcut(v) for v in value.get("shortcuts", ())),
        "driving_shortcuts": tuple(driver(v) for v in value.get("driving_shortcuts", ())),
        "formula_results": tuple(result(v) for v in value.get("formula_results", ())),
        "shortcut_order": tuple(value.get("shortcut_order", ())),
        "shortcut_edits": tuple(edit_context(v) for v in value.get("shortcut_edits", ())),
    }


def edit_context(value: dict[str, Any]) -> ShortcutEdit:
    from .storage import decode_entity

    data = dict(value, policy=policy(value["policy"]), targets=tuple(value["targets"]))
    data["opening"] = tuple(decode_entity(v) for v in value.get("opening", ()))
    data["bindings"] = tuple(override_binding(v) for v in value.get("bindings", ()))
    data["anchor"] = owner_anchor(value.get("anchor"))
    return ShortcutEdit(**data)


def owner_anchor(value: dict[str, Any] | None) -> OwnerAnchor | None:
    if value is None:
        return None
    return OwnerAnchor(
        **dict(value, fallback=tuple(value["fallback"]), parent_local=tuple(value["parent_local"]))
    )


def override_binding(value: dict[str, Any]) -> OverrideBinding:
    attachment = value["attachment"]
    return OverrideBinding(
        value["target"], Attachment(**dict(attachment, binding=tuple(attachment["binding"])))
    )
