"""Owned tissue phase evaluation; each phase consumes explicit accepted prerequisites."""

from typing import Any, cast

from anthroforge.core.tissue_diagnostics import TissueDiagnostic
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import topology
from anthroforge.native.mesh import Mesh

from . import tissue_construction, tissue_fields, tissue_relaxation, tissue_sources
from .tissue_output import TissueOutput


def accepted(resources: Any, result: Any, label: str) -> Mesh:
    if not result.asset or result.status in ("failed", "invalid", "cancelled"):
        raise ValueError(label + " has no usable accepted output.")
    return cast(Mesh, resources.meshes[result.asset].mesh)


def rest(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> TissueOutput:
    tissue_sources.require_result(item.base_result)
    tissue_fields.validate(resources, item, "BASE")
    return tissue_construction.construct(engine, resources, item, cancel)


def intrinsic(
    engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int
) -> TissueOutput:
    mesh = accepted(resources, item.rest_result, "Inflated rest")
    tissue_fields.validate(resources, item, "REST")
    if item.crop.enabled:
        raise ValueError("Tissue crop adapter is not yet available.")
    if item.relaxation.mode != "NONE" or item.constraints:
        return tissue_relaxation.evaluate(engine, document, resources, item, cancel)
    previous = resources.meshes.get(item.intrinsic_result.asset)
    return TissueOutput(
        mesh=topology.finalize(mesh, previous.mesh if previous else None, cancel),
        diagnostics=(TissueDiagnostic(),),
    )


def final(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> TissueOutput:
    mesh = accepted(resources, item.intrinsic_result, "Intrinsic tissue")
    if item.stacking:
        raise ValueError(
            "Tissue stacking adapter is not yet available; displaying current intrinsic output."
        )
    return TissueOutput(mesh=mesh)


EVALUATORS = dict(rest=rest, final=final)


def evaluate(
    engine: Any, document: Any, resources: Any, target: str, phase: str, cancel: int
) -> TissueOutput:
    item = document.object(target)
    if phase == "base":
        return tissue_sources.capture(engine, document, resources, item, cancel)
    if phase == "intrinsic":
        return intrinsic(engine, document, resources, item, cancel)
    return EVALUATORS[phase](engine, document, resources, item, cancel)
