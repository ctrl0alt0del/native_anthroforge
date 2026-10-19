"""Owned tissue phase evaluation; each phase consumes explicit accepted prerequisites."""

from typing import Any, cast

from anthroforge.core.tissues import TissueVCP
from anthroforge.native import topology
from anthroforge.native.mesh import Mesh

from . import tissue_construction, tissue_sources
from .tissue_output import TissueOutput


def accepted(resources: Any, result: Any, label: str) -> Mesh:
    if not result.asset or result.status in ("failed", "invalid", "cancelled"):
        raise ValueError(label + " has no usable accepted output.")
    return cast(Mesh, resources.meshes[result.asset].mesh)


def rest(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> Mesh:
    tissue_sources.require_result(item.base_result)
    if item.both_sides or len(item.parts) != 1:
        raise ValueError("Two-sided and branched tissue adapters are not yet available.")
    if item.parts[0].a.smoothing.mode != "OFF":
        raise ValueError("Tissue field/smoothing adapters are not yet available.")
    return tissue_construction.construct(engine, resources, item, cancel)


def intrinsic(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> Mesh:
    mesh = accepted(resources, item.rest_result, "Inflated rest")
    if item.relaxation.mode != "NONE" or item.constraints or item.crop.enabled:
        raise ValueError("Tissue relaxation, constraint and crop adapters are not yet available.")
    previous = resources.meshes.get(item.intrinsic_result.asset)
    return topology.finalize(mesh, previous.mesh if previous else None, cancel)


def final(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> Mesh:
    mesh = accepted(resources, item.intrinsic_result, "Intrinsic tissue")
    if item.stacking:
        raise ValueError(
            "Tissue stacking adapter is not yet available; displaying current intrinsic output."
        )
    return mesh


EVALUATORS = dict(rest=rest, intrinsic=intrinsic, final=final)


def evaluate(
    engine: Any, document: Any, resources: Any, target: str, phase: str, cancel: int
) -> TissueOutput:
    item = document.object(target)
    if phase == "base":
        return tissue_sources.capture(engine, document, resources, item, cancel)
    return TissueOutput(mesh=EVALUATORS[phase](engine, document, resources, item, cancel))
