"""Advisory decisions retain exact evidence signatures; freshness is independent."""

import hashlib
from dataclasses import asdict
from typing import Any

from anthroforge.core.object_outputs import output
from anthroforge.core.reconstruction import Review
from anthroforge.core.results import Port

from . import construction_policy, dependencies
from . import reconstruction_state as records

DIMENSIONS = ("ANATOMY", "ROUTE_COLLISION", "ATTACHMENT", "STACKING", "PERSISTENCE", "DISPLAY")
DECISIONS = ("PENDING", "APPROVED", "REJECTED", "NOT_APPLICABLE")


def signature(session: Any, subject: str, variant: str, stage: str) -> str:
    document = records.scene(session, variant)
    row = next((s for s in records.state(session).stages if s.id == stage), None)
    if row:
        return hashlib.sha256(repr(row).encode()).hexdigest()
    item = document.registry.anatomy.get(subject)
    if item is None:
        return "unavailable"
    role = output(item) if stage in ("geometry", "final") else stage
    ports = dependencies.ports(document, Port(subject, role)) | {Port(subject, "pose")}
    inputs = construction_policy.revisions(document, ports)
    return hashlib.sha256(repr((item, inputs)).encode()).hexdigest()


def decide(session: Any, subject: str, dimension: str, **options: Any) -> str:
    if set(options) - {"decision", "variant", "stage", "reviewer", "comment", "evidence"}:
        raise ValueError("Unknown review setting.")
    options["evidence"] = tuple(options.get("evidence", ()))
    variant, stage = options.get("variant", ""), options.get("stage", "final")
    records.subject(session, subject, variant)
    stamp = signature(session, subject, variant, stage)
    row = Review(subject, dimension, stamp, **options)
    validate(row)
    return str(records.upsert(session, "reviews", row))


def validate(row: Review) -> None:
    if row.dimension not in DIMENSIONS or row.decision not in DECISIONS:
        raise ValueError("Choose a supported review dimension and decision.")
    if row.decision != "PENDING" and not row.reviewer.strip():
        raise ValueError("Record who made this review decision.")


def inspect(session: Any, subject: str = "", variant: str | None = None) -> dict[str, Any]:
    rows = [r for r in records.state(session).reviews if not subject or r.subject == subject]
    rows = [r for r in rows if variant is None or r.variant == variant]
    return dict(
        dimensions=DIMENSIONS, decisions=DECISIONS, reviews=[describe(session, r) for r in rows]
    )


def describe(session: Any, row: Review) -> dict[str, Any]:
    try:
        stamp = signature(session, row.subject, row.variant, row.stage)
        freshness = "CURRENT" if stamp == row.signature else "OUTDATED"
    except ValueError:
        freshness = "UNAVAILABLE"
    return dict(asdict(row), freshness=freshness)


def execute(session: Any, operation: str, arguments: Any) -> Any:
    commands: dict[str, Any] = {"review.set": decide, "review.inspect": inspect}
    if operation not in commands:
        raise ValueError("Unknown review operation.")
    return commands[operation](session, **arguments)
