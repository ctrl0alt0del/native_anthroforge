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
    frame = stages.frame(context, item, stage)
    row = sample(context, item, options, cancel)
    config = accepted_settings(item, state)
    rows = constraint_rows(context, mesh, base, config, state, triangle, bary, cancel)
    report = point_report(context, item, options, row, config, state)
    report.update(constraints=rows, frame=frame)
    return dict(
        report=report, lines=native.face_lines(mesh, frame, triangle) + row["glyph"], mesh=mesh
    )


def sample(context: Any, item: Any, options: Any, cancel: int) -> Any:
    stage = options["stage"]
    mesh, state = stages.mesh(context, item.id, stage), stages.material(item, stage)
    base = context.resources.meshes.get(state.base) if state else None
    rest = context.resources.meshes.get(state.rest) if state else None
    query = options["triangle"], options["weights"]
    inputs = dict(
        rest=rest.mesh if rest else None, cancel=cancel, frame=stages.frame(context, item, stage)
    )
    return native.point(mesh, base.mesh if base else None, *query, **inputs)


def point_report(
    context: Any, item: Any, options: Any, row: Any, config: Any, state: Any
) -> dict[str, Any]:
    return dict(
        target=item.id,
        stage=options["stage"],
        asset=stages.result(item, options["stage"]).asset,
        triangle=options["triangle"],
        weights=list(options["weights"]),
        revision=context.document.revision,
        point=row,
        sources=sources(context, item),
        annotations=annotations(config, state, row),
    )


def accepted_settings(item: Any, state: Any) -> Any:
    if state is None:
        return item
    names = ("parts", "both_sides", "reverse", "relaxation", "crop", "constraints", "fields")
    return replace(item, **{name: getattr(state, name) for name in names})


def constraint_rows(
    context: Any, mesh: Any, base: Any, item: Any, state: Any, triangle: int, bary: Any, cancel: int
) -> list[Any]:
    if state is None or not item.constraints:
        return []
    rest = context.resources.meshes[state.rest].mesh
    values = native.regions(mesh, rest, base.mesh if base else None, triangle, bary, item, cancel)
    return [
        constraint_record(c, v)
        for c, v in zip(item.constraints, values, strict=True)
        if v[1] > 1e-8
    ]


def constraint_record(constraint: Any, values: Any) -> dict[str, Any]:
    return dict(
        id=constraint.id,
        mask=constraint.mask,
        mode=constraint.mode,
        core=values[0],
        influence=values[1],
        fixed_fraction=values[2],
        strength=values[3],
        offset=constraint.offset,
        target=asdict(constraint.reference) if constraint.reference else None,
    )


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
        result.append(
            "Crop/generated boundary: not an anatomical attachment or zero-height constraint."
        )
    return result


def smoothing_annotations(item: Any, point: Any) -> list[str]:
    part = point["part"]
    if part < 0 or part >= len(item.parts) or point["side"] not in (1, 2):
        return []
    side = item.parts[part].a if point["side"] == 1 else item.parts[part].b
    if side.smoothing.mode == "OFF":
        return ["Height smoothing is off for this side."]
    reasons = smoothing_reasons(point)
    return (
        ["Height smoothing retains " + ", ".join(reasons) + "."]
        if reasons
        else ["No fixed height boundary is identified at this location."]
    )


def smoothing_reasons(point: Any) -> list[str]:
    return [
        label
        for key, label in (
            ("source_boundary", "boundary"),
            ("seam", "seam"),
            ("zero_height", "zero-height rest samples"),
        )
        if point[key] > 0
    ]


def sources(context: Any, item: Any) -> list[dict[str, Any]]:
    source = context.document.object(item.source)
    keys = [s.curve for s in source.curves] if isinstance(source, Surface) else [source.id]
    records = [context.document.object(key) for key in keys]
    return [
        dict(
            id=o.id,
            name=o.name,
            bindings=[asdict(b) for b in o.bindings] if isinstance(o, Fiber) else [],
        )
        for o in records
    ]
