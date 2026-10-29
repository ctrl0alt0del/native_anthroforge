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
        if row.subject != subject or row.variant != variant:
            raise ValueError("Stage does not belong to this subject and variant.")
        return hashlib.sha256(repr(row).encode()).hexdigest()
    if stage not in ("geometry", "base", "rest", "intrinsic", "final", "fibers"):
        raise ValueError("Choose an available reconstruction stage.")
    return live_signature(document, subject, stage)


def live_signature(document: Any, subject: str, stage: str) -> str:
    item = document.registry.anatomy.get(subject)
    if item is None:
        raise ValueError("The reviewed anatomical instance is unavailable.")
    role = output(item) if stage in ("geometry", "final") else stage
    ports = dependencies.ports(document, Port(subject, role)) | {Port(subject, "pose")}
    inputs = construction_policy.revisions(document, ports)
    return hashlib.sha256(repr((item, inputs)).encode()).hexdigest()


def decide(session: Any, subject: str, dimension: str, **options: Any) -> str:
    if set(options) - {"decision", "variant", "stage", "reviewer", "comment", "evidence", "region"}:
        raise ValueError("Unknown review setting.")
    options["evidence"] = tuple(options.get("evidence", ()))
    variant, stage = options.get("variant", ""), options.get("stage", "final")
    records.subject(session, subject, variant)
    stamp = stamped(session, subject, variant, stage, options.get("region", ""))
    row = Review(subject, dimension, stamp, **options)
    validate(row)
    for key in row.evidence:
        records.selected(session, "evidence", key)
    return str(records.upsert(session, "reviews", row))


def stamped(session: Any, subject: str, variant: str, stage: str, region: str = "") -> str:
    stamp = signature(session, subject, variant, stage)
    if not region:
        return stamp
    from .reconstruction_regions import inspect

    row = inspect(session, region)
    if row["target"] != subject or row["variant"] != variant or not row["available"]:
        raise ValueError("Choose an available region belonging to this anatomy and variant.")
    return hashlib.sha256(repr((stamp, row)).encode()).hexdigest()


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
        stamp = stamped(session, row.subject, row.variant, row.stage, row.region)
        freshness = "CURRENT" if stamp == row.signature else "OUTDATED"
    except ValueError:
        freshness = "UNAVAILABLE"
    return dict(asdict(row), freshness=freshness)


def execute(session: Any, operation: str, arguments: Any) -> Any:
    commands: dict[str, Any] = {"review.set": decide, "review.inspect": inspect}
    if operation not in commands:
        raise ValueError("Unknown review operation.")
    return commands[operation](session, **arguments)
