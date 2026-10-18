"""Actual cycle participants and downstream effects share output-level evidence."""

from dataclasses import replace
from threading import Event
from typing import Any

from anthroforge.core.document import Document
from anthroforge.core.issues import Issue, evidence, fingerprint
from anthroforge.core.results import Port

from ..dependency_inspection import cycle_records

BLOCKED = Issue(
    "dependencies.v1",
    "document",
    "DEPENDENCY_BLOCKED",
    "Blocked by an upstream cycle",
    severity="error",
)
PARTICIPANT_DETAILS = (
    "This output belongs to member_component. The cycles list also includes upstream causes. "
    "Accepted output is retained."
)
DOWNSTREAM_DETAILS = (
    "This output is outside the cycle and is blocked by the listed upstream cycle components. "
    "Accepted output is retained."
)


def check(document: Document, scope: str, cancel: Event) -> tuple[Issue, ...]:
    graph = document.index.structure.dependencies
    rows = []
    for port in sorted(graph.blocked, key=lambda p: (p.owner, p.output)):
        if cancel.is_set():
            break
        rows.append(finding(document, port))
    return tuple(rows)


def finding(document: Document, port: Port) -> Issue:
    context = cycle_records(document, port)
    return replace(
        BLOCKED,
        **labels(context),
        target=port.owner,
        kind="SCP" if port.owner in document.index.entities else "CONTROL",
        stage=port.output,
        source=fingerprint(context),
        local_key=port.owner,
        related=tuple(sorted({p["owner"] for group in context["cycles"] for p in group})),
        evidence=evidence(**context),
    )


def labels(context: dict[str, Any]) -> dict[str, str]:
    if context["participant"]:
        return dict(
            code="DEPENDENCY_CYCLE",
            summary="This output participates in a dependency cycle",
            details=PARTICIPANT_DETAILS,
        )
    return dict(details=DOWNSTREAM_DETAILS)
