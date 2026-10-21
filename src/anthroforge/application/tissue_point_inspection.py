"""Explain accepted material samples without pretending to recover solver causality."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.fibers import Fiber
from anthroforge.core.surfaces import Surface
from anthroforge.native import inspection as native

from . import tissue_inspection_stages as stages


def explain(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    stage, triangle, bary = options["stage"], int(options["triangle"]), options["weights"]
    item, mesh = stages.tissue(context, target), stages.mesh(context, target, stage)
    state = stages.material(item, stage)
    base = context.resources.meshes.get(state.base) if state else None
    row = native.point(mesh, base.mesh if base else None, triangle, bary)
    config = accepted_settings(item, state)
    rows = constraint_rows(context, mesh, base, config, state, triangle, bary, cancel)
    frame = stages.frame(context, item, stage)
    report = dict(target=target, stage=stage, asset=stages.result(item, stage).asset,
                  triangle=triangle, weights=list(bary), revision=context.document.revision, point=row,
                  constraints=rows, sources=sources(context, item), annotations=annotations(config, state, row), frame=frame)
    return dict(report=report, lines=native.face_lines(mesh, frame, triangle), mesh=mesh)


def accepted_settings(item: Any, state: Any) -> Any:
    if state is None:
        return item
    names = ("parts", "both_sides", "reverse", "relaxation", "crop", "constraints", "fields")
    return replace(item, **{name: getattr(state, name) for name in names})


def constraint_rows(context: Any, mesh: Any, base: Any, item: Any, state: Any, triangle: int, bary: Any, cancel: int) -> list[Any]:
    if state is None or not item.constraints:
        return []
    rest = context.resources.meshes[state.rest].mesh
    values = native.regions(mesh, rest, base.mesh if base else None, triangle, bary, item, cancel)
    return [dict(id=c.id, mask=c.mask, mode=c.mode, core=v[0], influence=v[1], fixed_fraction=v[2],
                 strength=v[3], offset=c.offset, target=asdict(c.reference) if c.reference else None)
            for c, v in zip(item.constraints, values, strict=True) if v[1] > 1e-8]


def annotations(item: Any, state: Any, point: Any) -> list[str]:
    result = []
    if point["backing"] > 0:
        result.append("Structural backing: exact constraint during relaxation and stacking.")
    if point["source_boundary"] > 0:
        result.append("Construction boundary contributes to this location.")
    if point["seam"] > 0:
        result.append("Shared material seam contributes to this location.")
    result.extend(smoothing_annotations(item, point))
    if state and state.crop.enabled and point["boundary"] and point["source_boundary"] < 1 - 1e-8:
        result.append("Crop/generated boundary: not an anatomical attachment or zero-height constraint.")
    return result


def smoothing_annotations(item: Any, point: Any) -> list[str]:
    part = point["part"]
    if part < 0 or part >= len(item.parts) or point["side"] not in (1, 2):
        return []
    side = item.parts[part].a if point["side"] == 1 else item.parts[part].b
    if side.smoothing.mode == "OFF":
        return ["Height smoothing is off for this side."]
    reasons = [label for key, label in (("source_boundary", "boundary"), ("seam", "seam"), ("zero_height", "zero-height samples")) if point[key] > 0]
    return ["Height smoothing retains " + ", ".join(reasons) + "."] if reasons else ["No fixed height boundary is identified at this location."]


def sources(context: Any, item: Any) -> list[dict[str, Any]]:
    source = context.document.object(item.source)
    keys = [s.curve for s in source.curves] if isinstance(source, Surface) else [source.id]
    records = [context.document.object(key) for key in keys]
    return [dict(id=o.id, name=o.name, bindings=[asdict(b) for b in o.bindings] if isinstance(o, Fiber) else []) for o in records]
