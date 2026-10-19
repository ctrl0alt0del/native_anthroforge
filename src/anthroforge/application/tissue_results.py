"""Stage publications own provenance and distinguish intrinsic display from final readiness."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP

from .assets import Asset
from .evaluation_results import accepted_result


def install(session: Any, item: TissueVCP) -> None:
    session.replace_document(
        objects=tuple(item if o.id == item.id else o for o in session.document.objects)
    )


def publish(session: Any, document: Any, target: str, phase: str, mesh: Any, ports: Any) -> None:
    current = session.document.object(target)
    key = str(uuid4())
    session.assets[key] = Asset(mesh, "generated tissue " + phase, "", 1.0, False)
    before = replace(
        current,
        result=getattr(current, phase + "_result"),
        construction_revision=getattr(current, phase + "_revision"),
    )
    result = accepted_result(document, before, ports, key)
    changes = {phase + "_result": result}
    if phase in ("intrinsic", "final"):
        changes["result"] = replace(result, status="unstacked" if phase == "intrinsic" else "ready")
    install(session, replace(current, **changes))


def fail(session: Any, target: str, phase: str, error: str) -> None:
    item = session.document.registry.authored.get(target)
    if not isinstance(item, TissueVCP):
        return
    result = replace(getattr(item, phase + "_result"), status="failed", error=error)
    fallback = (
        phase == "final"
        and bool(item.intrinsic_result.asset)
        and item.intrinsic_result.status == "ready"
    )
    display = replace(item.result, status="unstacked" if fallback else "failed", error=error)
    install(session, replace(item, **{phase + "_result": result, "result": display}))


def pending(item: TissueVCP, phases: set[str]) -> TissueVCP:
    changes = {
        phase + "_result": replace(getattr(item, phase + "_result"), status="pending")
        for phase in PHASES
        if phase in phases
    }
    return replace(item, result=replace(item.result, status="pending"), **changes)
