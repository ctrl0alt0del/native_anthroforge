"""Conservative equality of definitions for reusing cross-record validation.

Record constructors still validate every new value. Only known evaluation bookkeeping
is excluded here; new authored fields invalidate validation unless explicitly qualified.
Stack plans are included because their providers change dependency edges.
"""

from dataclasses import fields
from typing import Any

EVALUATED = frozenset(
    {
        "generation",
        "pose_revision",
        "construction_revision",
        "result_generation",
        "pose_receipt",
        "result",
        "status",
        "error",
        "base_state",
        "diagnostics",
        "accepted_kind",
        "accepted_parts",
        "base_revision",
        "rest_revision",
        "intrinsic_revision",
        "plan_revision",
        "final_revision",
        "base_result",
        "rest_result",
        "intrinsic_result",
        "plan_result",
        "final_result",
        "rest_material",
        "intrinsic_material",
        "final_material",
        "resolved_position",
        "resolved_frame",
    }
)


def definition_fields(kind: type[Any]) -> tuple[str, ...]:
    return tuple(field.name for field in fields(kind) if field.name not in EVALUATED)


def same(before: Any, after: Any) -> bool:
    if before is after:
        return True
    return type(before) is type(after) and all(
        getattr(before, name) == getattr(after, name) for name in definition_fields(type(after))
    )


def records_match(records: Any, previous: Any) -> bool:
    return len(records) == len(previous) and all(
        item.id in previous and same(previous[item.id], item) for item in records
    )
