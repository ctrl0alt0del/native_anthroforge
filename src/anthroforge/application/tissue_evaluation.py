"""Owned tissue phase evaluation; each phase consumes explicit accepted prerequisites."""

from dataclasses import replace
from typing import Any, cast

from anthroforge.core.tissue_diagnostics import TissueDiagnostic
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import tissue_crop, topology
from anthroforge.native.mesh import Mesh

from . import (
    tissue_construction,
    tissue_fields,
    tissue_materials,
    tissue_relaxation,
    tissue_sources,
    tissue_stack_evaluation,
)
from .tissue_output import TissueOutput


def accepted(resources: Any, result: Any, label: str) -> Mesh:
    if not result.asset or result.status in ("failed", "invalid", "cancelled"):
        raise ValueError(label + " has no usable accepted output.")
    return cast(Mesh, resources.meshes[result.asset].mesh)


def rest(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> TissueOutput:
    tissue_sources.require_result(item.base_result)
    tissue_fields.validate(resources, item, "BASE")
    return tissue_construction.construct(engine, resources, item, cancel)


def uncropped(
    engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int
) -> TissueOutput:
    mesh = accepted(resources, item.rest_result, "Inflated rest")
    tissue_fields.validate(resources, item, "REST")
    if item.relaxation.mode != "NONE" or item.constraints:
        return tissue_relaxation.evaluate(engine, document, resources, item, cancel)
    previous = resources.meshes.get(item.intrinsic_result.asset)
    return TissueOutput(
        mesh=topology.finalize(mesh, previous.mesh if previous else None, cancel),
        diagnostics=(TissueDiagnostic(),),
    )


def intrinsic(
    engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int
) -> TissueOutput:
    item = tissue_materials.effective(item)
    output = uncropped(engine, document, resources, item, cancel)
    if not item.crop.enabled:
        return output
    assert output.mesh is not None
    base = resources.meshes[item.base_result.asset].mesh
    return replace(output, mesh=tissue_crop.evaluate(base, output.mesh, item.crop, cancel))


def final(engine: Any, document: Any, resources: Any, item: TissueVCP, cancel: int) -> TissueOutput:
    mesh = accepted(resources, item.intrinsic_result, "Intrinsic tissue")
    if item.stacking:
        tissue_sources.require_result(item.plan_result)
        return tissue_stack_evaluation.evaluate(engine, document, resources, item, cancel)
    return TissueOutput(mesh=mesh)


EVALUATORS = dict(rest=rest, plan=tissue_stack_evaluation.plan, final=final)


def evaluate(
    engine: Any, document: Any, resources: Any, target: str, phase: str, cancel: int
) -> TissueOutput:
    item = document.object(target)
    if phase == "base":
        return tissue_sources.capture(engine, document, resources, item, cancel)
    evaluator = intrinsic if phase == "intrinsic" else EVALUATORS[phase]
    output = evaluator(engine, document, resources, item, cancel)
    output = replace(output, material=tissue_materials.capture(engine, document, item, phase))
    return reuse(resources, item, phase, output, cancel)


def reuse(resources: Any, item: Any, phase: str, output: TissueOutput, cancel: int) -> TissueOutput:
    key = getattr(item, phase + "_result").asset
    before = resources.meshes.get(key)
    if (
        output.mesh is not None
        and before
        and topology.same_content(output.mesh, before.mesh, cancel)
    ):
        return replace(output, mesh=None, asset=key)
    return output
