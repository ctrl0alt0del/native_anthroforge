"""Skin target planning; execution and queues remain owned by the task coordinator."""

from dataclasses import dataclass
from enum import StrEnum


class Condition(StrEnum):
    READY = "ready"
    MISSING = "missing"
    STALE = "stale"
    INCOMPATIBLE = "incompatible"
    WAITING = "waiting"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    EMPTY = "empty"


@dataclass(frozen=True, slots=True)
class Assessment:
    condition: Condition = Condition.READY
    reason: str = ""


@dataclass(frozen=True, slots=True)
class Inputs:
    sources: Assessment
    draft: Assessment
    topology: Assessment
    reference: Assessment
    final_current: bool


@dataclass(frozen=True, slots=True)
class Plan:
    stage: str = ""
    reason: str = ""


class RepairRequired(ValueError):
    """A typed worker compatibility failure; numerical failure never implies repair."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(reason)
        self.stage = stage


def plan(mode: str, inputs: Inputs, handoff: bool = False) -> Plan:
    if inputs.sources.condition != Condition.READY:
        return Plan(reason=inputs.sources.reason)
    if mode == "DRAFT":
        return draft_plan(inputs.draft)
    if mode != "FINAL":
        raise ValueError("Unknown skin target mode.")
    if handoff and inputs.draft.condition != Condition.READY:
        return draft_plan(inputs.draft)
    return final_plan(inputs)


def draft_plan(draft: Assessment) -> Plan:
    if draft.condition in (Condition.MISSING, Condition.STALE, Condition.INCOMPATIBLE):
        return Plan("envelope", draft.reason)
    return Plan(reason=draft.reason)


def final_plan(inputs: Inputs) -> Plan:
    reference = inputs.reference
    if reference.condition == Condition.READY:
        return Plan() if inputs.final_current else Plan("deformation")
    if reference.condition == Condition.INCOMPATIBLE:
        return Plan("construction", reference.reason)
    if reference.condition != Condition.MISSING:
        return Plan(reason=reference.reason)
    if inputs.topology.condition == Condition.READY:
        return Plan("reference", reference.reason)
    if inputs.draft.condition == Condition.READY:
        return Plan("downstream", inputs.topology.reason)
    if draft_plan(inputs.draft).stage:
        return Plan("construction", inputs.draft.reason)
    return Plan(reason=inputs.draft.reason)
