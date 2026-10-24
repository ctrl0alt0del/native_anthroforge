"""Cheap structural mirror findings are independent of reflected geometry readiness."""

from dataclasses import asdict
from threading import Event
from typing import Any

from anthroforge.core.issues import Issue, fingerprint

from .. import mirror_bindings
from .providers import Provider


def source(document: Any, scope: str) -> Any:
    return repr(document.mirrors.signature), tuple(
        asdict(v) for v in document.shared_mirror_targets
    )


def check(document: Any, scope: str, cancel: Event) -> tuple[Issue, ...]:
    result = [conflict(document, key) for key in document.mirrors.conflicts]
    for instance in document.mirrors.instances.values():
        if cancel.is_set():
            break
        result.extend(
            missing(document, row)
            for row in mirror_bindings.rows(document, instance)
            if row["status"] == "missing"
        )
    return tuple(result)


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
        "MIRROR_ATTACHMENT_TARGET_MISSING",
        document.object(row["source"]).name + ": mirrored attachment target is unresolved",
        target=row["source"],
        local_key=row["instance"] + ":" + row["binding"],
        details=row["error"] + " Exact reflected geometry remains available.",
        source=fingerprint(row),
        related=(row["reference"]["target"],),
    )


def provider() -> Provider:
    return Provider(
        "mirroring.v1",
        lambda d: {"document"} if d.mirror_rules else set(),
        lambda d, c: {"document"} if c.document or c.objects or c.entities or c.controls else set(),
        source,
        check,
    )
