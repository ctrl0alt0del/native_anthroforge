"""Resumable human/API ownership; no numerical scheduler or autonomous work runner."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.reconstruction import ReconstructionWork

from . import reconstruction_state as records
from .operations import require_name

STATUSES = ("TODO", "ACTIVE", "PAUSED", "BLOCKED", "COMPLETE")


def add(
    session: Any, subject: str, type_id: str = "", variant: str = "", next_action: str = ""
) -> str:
    records.subject(session, subject, variant)
    type_id = type_id or assigned_type(session, subject)
    if type_id:
        records.selected(session, "types", type_id)
    return str(
        records.upsert(
            session,
            "work",
            ReconstructionWork(subject, type_id, next_action=next_action, variant=variant),
        )
    )


def assigned_type(session: Any, subject: str) -> str:
    return next((r.type_id for r in records.state(session).assignments if r.target == subject), "")


def scope(row: Any) -> str:
    return str(row.type_id or row.subject)


def claim(session: Any, owner: str, work: str = "", takeover: bool = False) -> dict[str, Any]:
    require_name(owner)
    rows = records.state(session).work
    selected = records.selected(session, "work", work) if work else available(rows, owner)
    if selected is None:
        return dict(work=None)
    locked = conflicting_owners(rows, selected, owner)
    return take_claim(session, rows, selected, locked, owner, takeover)


def conflicting_owners(rows: Any, selected: Any, owner: str) -> list[Any]:
    return [
        r
        for r in rows
        if scope(r) == scope(selected) and r.owner and r.owner != owner and r.status != "COMPLETE"
    ]


def take_claim(
    session: Any, rows: Any, selected: Any, locked: Any, owner: str, takeover: bool
) -> dict[str, Any]:
    if locked and not takeover:
        raise ValueError(
            "This anatomical type is claimed. Take over explicitly to change its owner."
        )
    replacements = {r.id: replace(r, owner=owner) for r in locked} if takeover else {}
    row = replace(selected, owner=owner, status="ACTIVE", blocker="")
    replacements[row.id] = row
    records.install(session, work=tuple(replacements.get(r.id, r) for r in rows))
    return asdict(row)


def available(rows: Any, owner: str) -> Any:
    blocked = {scope(r) for r in rows if r.owner and r.owner != owner and r.status != "COMPLETE"}
    return next((r for r in rows if r.status == "TODO" and scope(r) not in blocked), None)


def update(session: Any, work: str, owner: str, status: str, **changes: Any) -> None:
    if set(changes) - {"next_action", "blocker", "approach", "checkpoint"}:
        raise ValueError("Unknown work setting.")
    row = records.selected(session, "work", work)
    if not owner or row.owner != owner:
        raise ValueError("Claim this work or explicitly take over before updating it.")
    row = replace(row, status=status, owner="" if status == "TODO" else owner, **changes)
    validate(session, row)
    records.upsert(session, "work", row)


def validate(session: Any, row: Any) -> None:
    if row.status not in STATUSES:
        raise ValueError("Unknown queue status.")
    if row.status == "BLOCKED" and not row.blocker.strip():
        raise ValueError("Describe the blocker before blocking work.")
    if row.checkpoint and not records.state(session).variant(row.checkpoint).checkpoint:
        raise ValueError("Choose an immutable checkpoint for resumable work.")


def inspect(session: Any) -> dict[str, Any]:
    return dict(
        statuses=STATUSES, work=[describe(session, row) for row in records.state(session).work]
    )


def describe(session: Any, row: Any) -> dict[str, Any]:
    try:
        name = records.subject(session, row.subject, row.variant).name
    except ValueError:
        name = "Unavailable anatomy"
    return dict(asdict(row), name=name)


def execute(session: Any, operation: str, arguments: Any) -> Any:
    commands: dict[str, Any] = {"add": add, "claim": claim, "update": update, "inspect": inspect}
    name = operation.removeprefix("reconstruction.queue.")
    if name not in commands:
        raise ValueError("Unknown reconstruction queue operation.")
    return commands[name](session, **arguments)
