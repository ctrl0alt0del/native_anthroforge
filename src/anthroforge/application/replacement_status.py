"""Replacement action providers reuse the exact guards used to assess and commit."""

from dataclasses import asdict
from functools import partial
from typing import Any

from . import operation_status


def validate_start(session: Any, slot: str, target: str) -> None:
    if session.history.before is not None or session.waiting_save:
        action = (
            "replacing a source mesh" if slot == "mesh_replacement" else "changing a tissue source"
        )
        raise ValueError("Finish the current edit before " + action + ".")
    validate_target(session, slot, target)


def validate_target(session: Any, slot: str, target: str) -> None:
    from .mesh_replacement import selected
    from .tissue_operations import tissue

    if not target:
        raise ValueError(
            "Select an imported SCP." if slot == "mesh_replacement" else "Select a Tissue."
        )
    (selected if slot == "mesh_replacement" else tissue)(session, target)


def assess(session: Any, slot: str, target: str) -> operation_status.Eligibility:
    return operation_status.assess(partial(validate_start, session, slot, target))


def application(session: Any, slot: str) -> operation_status.Eligibility:
    from .replacement_assessments import ready

    value = getattr(session, slot)
    return operation_status.assess(partial(ready, session, slot, value.token))


def describe(session: Any, slot: str, target: str) -> dict[str, Any]:
    return dict(
        start=asdict(assess(session, slot, target)), apply=asdict(application(session, slot))
    )
