"""Schema-four persistent intent and accepted dependency decisions."""

from typing import Any

from anthroforge.core.tissue_stacking import StackOrder, StackPlan, StackRelationship, StackSettings


def decode(state: dict[str, Any]) -> None:
    state["stack_settings"] = StackSettings(**state.get("stack_settings", {}))
    state["stack_relationships"] = tuple(
        StackRelationship(**dict(row, regions=tuple(tuple(v) for v in row.get("regions", ()))))
        for row in state.get("stack_relationships", ())
    )
    data = state.get("stack_plan", {})
    state["stack_plan"] = StackPlan(
        tuple(data.get("providers", ())),
        tuple(StackOrder(**row) for row in data.get("orders", ())),
        data.get("error", ""),
    )
