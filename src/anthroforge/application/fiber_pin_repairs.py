"""Explicitly approved pin proposals validate together and share one undo transaction."""

import json
from dataclasses import replace
from typing import Any

from anthroforge.core.entities import Attachment
from anthroforge.core.fibers import FiberBinding
from anthroforge.core.issues import fingerprint

from . import curve_edit_state
from .fiber_support_operations import selected
from .issues import fiber_pins
from .issues.resolution import Repair
from .object_operations import editable, install


def require_proposal(session: Any, identity: str) -> Any:
    issue = session.issues.repository.records.get(identity)
    if issue is None or issue.provider != fiber_pins.NAME or issue.code != fiber_pins.REPAIR:
        raise ValueError("Choose an available Fiber pin-repair proposal.")
    state = session.issues.repository.states.get((issue.provider, issue.scope))
    stamp = fingerprint(fiber_pins.source(session.document, issue.scope))
    if not state or state.status != "COMPLETE" or issue.source != stamp:
        raise ValueError("The pin-repair proposal is stale; check pins again.")
    editable(session, issue.target)
    return issue


def proposed(session: Any, identity: str) -> tuple[Any, Any]:
    issue = require_proposal(session, identity)
    data = json.loads(issue.evidence)["proposal"]
    record = Attachment(child_mode="OBJECT_ORIGIN", binding=tuple(data["binding"]))
    binding = FiberBinding(
        data["point"],
        data["target"],
        record,
        role=data["role"],
        instance=data.get("instance", ""),
        material_asset=data["material_asset"],
    )
    return issue, binding


def apply(session: Any, identities: list[str]) -> list[str]:
    if not identities or len(set(identities)) != len(identities):
        raise ValueError("Select distinct pin-repair proposals to approve.")
    values = [proposed(session, identity) for identity in identities]
    groups = {issue.target for issue, _ in values}
    before = set(session.scheduler.registry.by_id)
    changes = [replacement(session, target, values) for target in sorted(groups)]
    for item in changes:
        install(session, item)
    jobs = tuple(session.scheduler.registry.by_id.keys() - before)
    track(session, values, jobs)
    return list(jobs)


def replacement(session: Any, target: str, values: Any) -> Any:
    item = selected(session, target)
    changes = {binding.point: binding for issue, binding in values if issue.target == target}
    if set(changes) - {b.point for b in item.bindings}:
        raise ValueError("A proposed pin no longer exists; check pins again.")
    bindings = replaced_bindings(item, changes)
    edit = repaired_edit(session, item, changes)
    current = curve_edit_state.current(session, item)
    return replace(current, bindings=bindings, edit=edit)


def replaced_bindings(item: Any, changes: Any) -> Any:
    return tuple(
        replace(changes[b.point], capture_scope=b.capture_scope) if b.point in changes else b
        for b in item.bindings
    )


def repaired_edit(session: Any, item: Any, changes: Any) -> Any:
    edit = item.edit or curve_edit_state.baseline(session, item)
    return replace(
        edit,
        shape=False,
        rebind=tuple(p for p in edit.rebind if p not in changes),
        offsets=tuple(p for p in edit.offsets if p not in changes),
    )


def track(session: Any, values: Any, jobs: tuple[str, ...]) -> None:
    for issue, _ in values:
        session.issues.resolution.running[issue.id] = Repair(issue, "pin_rebind", jobs)
    session.issues.repository.revision += 1
