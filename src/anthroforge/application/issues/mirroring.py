"""Cheap structural mirror findings are independent of reflected geometry readiness."""

from dataclasses import asdict
from threading import Event
from typing import Any

from anthroforge.core.issues import Issue, fingerprint

from .. import mirror_bindings
from .providers import Provider


def source(document: Any, scope: str) -> Any:
    return repr(document.mirrors.signature), repr(shared_state(document))


def shared_state(document: Any) -> Any:
    return tuple(
        (
            asdict(v),
            document.object(v.source),
            tuple(
                document.object(ref.target)
                for _, ref in mirror_bindings.references(document.object(v.source))
            ),
        )
        for v in document.shared_mirror_targets
    )


def check(document: Any, scope: str, cancel: Event) -> tuple[Issue, ...]:
    context, document = document, document.document
    result = [conflict(document, key) for key in document.mirrors.conflicts]
    for instance in document.mirrors.instances.values():
        if cancel.is_set():
            break
        result.extend(
            missing(document, row)
            for row in checked_rows(context, instance)
            if row["status"] in ("missing", "mismatch")
        )
        result.extend(junction_findings(document, instance))
    return tuple(result)


def junction_findings(document: Any, instance: Any) -> Any:
    from ..mirror_junctions import describe

    return tuple(
        junction_issue(document, instance, row, member)
        for row in describe(document, instance)
        for member in row["members"]
        if not member["available"]
    )


def junction_issue(document: Any, instance: Any, row: Any, member: Any) -> Issue:
    return Issue(
        "mirroring.v1",
        "document",
        "MIRROR_JUNCTION_MEMBER_MISSING",
        "Mirrored junction has an unavailable member",
        target=instance.source,
        local_key=row["id"] + ":" + member["curve"],
        source=fingerprint(row),
        related=(member["curve"],),
        details="Align the member's inherited rule or plane override. "
        "Exact reflected geometry remains available.",
    )


def checked_rows(context: Any, instance: Any) -> Any:
    from ..mirror_attachment_checks import validate

    return validate(context, instance, mirror_bindings.rows(context.document, instance))


def conflict(document: Any, target: str) -> Issue:
    return Issue(
        "mirroring.v1",
        "document",
        "MIRROR_PLANE_CONFLICT",
        "Construction inherits incompatible mirror planes",
        target=target,
        source=fingerprint(source(document, "document")),
        local_key=target,
        details="Choose an explicit construction plane override; no parent was chosen implicitly.",
    )


def missing(document: Any, row: Any) -> Issue:
    return Issue(
        "mirroring.v1",
        "document",
        "MIRROR_ATTACHMENT_MISMATCH"
        if row["status"] == "mismatch"
        else "MIRROR_ATTACHMENT_TARGET_MISSING",
        document.object(row["source"]).name + ": mirrored attachment relationship needs attention",
        target=row["source"],
        local_key=row["instance"] + ":" + row["binding"],
        details=row["error"] + " Exact reflected geometry remains available.",
        source=fingerprint(row),
        related=(row["reference"]["target"],),
    )


def provider(session: Any) -> Provider:
    from ..inspection_context import freeze

    return Provider(
        "mirroring.v1",
        lambda d: {"document"} if d.mirror_rules else set(),
        lambda d, c: {"document"} if c.document or c.objects or c.entities or c.controls else set(),
        source,
        check,
        lambda _: freeze(session),
    )
