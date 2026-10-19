"""Stage publications own provenance and distinguish intrinsic display from final readiness."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP

from .assets import Asset
from .evaluation_results import accepted_result
from .tissue_materials import accepted as accepted_material
from .tissue_output import TissueOutput


def install(session: Any, item: TissueVCP) -> None:
    session.replace_document(
        objects=tuple(item if o.id == item.id else o for o in session.document.objects)
    )


def publish(
    session: Any, document: Any, target: str, phase: str, output: TissueOutput, ports: Any
) -> None:
    current = session.document.object(target)
    key = register(session, output, phase)
    result = accept(document, current, phase, ports, key)
    install(session, replace(current, **publication(current, phase, result, output)))


def publication(
    current: TissueVCP, phase: str, result: Any, output: TissueOutput
) -> dict[str, Any]:
    changes: dict[str, Any] = {phase + "_result": result}
    if output.base is not None:
        changes["base_state"] = output.base
    changes.update(material_changes(output, phase, result.asset))
    if output.diagnostics is not None:
        changes["diagnostics"] = (
            *[d for d in current.diagnostics if d.stage != phase],
            *output.diagnostics,
        )
    if phase in ("intrinsic", "final"):
        changes["result"] = replace(result, status="unstacked" if phase == "intrinsic" else "ready")
    return changes


def material_changes(output: TissueOutput, phase: str, asset: str) -> dict[str, Any]:
    if output.material is None:
        return {}
    return {phase + "_material": accepted_material(output.material, phase, asset)}


def accept(document: Any, item: TissueVCP, phase: str, ports: Any, key: str) -> Any:
    before = replace(
        item,
        result=getattr(item, phase + "_result"),
        construction_revision=getattr(item, phase + "_revision"),
    )
    return accepted_result(document, before, ports, key)


def register(session: Any, output: TissueOutput, phase: str) -> str:
    if output.mesh is None:
        return output.asset
    key = str(uuid4())
    session.assets[key] = Asset(output.mesh, "generated tissue " + phase, "", 1.0, False)
    return key


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
