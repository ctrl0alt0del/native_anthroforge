"""Serializable assembly inventory and findings shared by desktop and headless clients."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.object_registry import kind


def inventory(source: Any) -> list[dict[str, Any]]:
    if source is None:
        return []
    anatomy = source.document.registry.anatomy
    return [
        dict(id=k, name=v.name, kind=kind(v), anatomy=k in anatomy, parent=getattr(v, "parent", ""))
        for k, v in source.document.registry.records.items()
    ]


def describe(manager: Any) -> dict[str, Any]:
    source, value = manager.source, manager.preparation
    return dict(
        source=source.token,
        source_state=source.state,
        source_error=source.error,
        token=value.token,
        state=value.state,
        error=value.error,
        job_id=value.job or source.job,
        inventory=source.inventory,
        **candidate_details(value.candidate),
    )


def candidate_details(candidate: Any) -> dict[str, Any]:
    if candidate is None:
        return {}
    return dict(
        ready=candidate.ready,
        findings=list(candidate.findings),
        evidence=list(candidate.evidence),
        selection=candidate.selection,
        references=[asdict(r) for r in candidate.references],
        mappings=candidate.mappings,
    )
