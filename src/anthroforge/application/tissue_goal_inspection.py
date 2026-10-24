"""Explain current constraint goals against an accepted stage with explicit provenance."""

from dataclasses import replace
from typing import Any

from anthroforge.native import inspection_goals as native

from . import tissue_inspection_stages as stages
from . import tissue_region_goals, tissue_relaxation


def enrich(
    context: Any, item: Any, state: Any, options: Any, payload: dict[str, Any], cancel: int
) -> dict[str, Any]:
    if state is None or not payload["report"]["constraints"]:
        return payload
    try:
        rows = calculate(context, item, state, options, cancel)
        attach(payload, item, rows)
    except ValueError as error:
        payload["report"]["goal_error"] = str(error)
    return payload


def accepted(item: Any, state: Any) -> Any:
    return replace(
        item,
        base_state=state.base_state,
        base_result=replace(item.base_result, asset=state.base),
        rest_result=replace(item.rest_result, asset=state.rest),
    )


def calculate(context: Any, item: Any, state: Any, options: Any, cancel: int) -> Any:
    item = accepted(item, state)
    engine, document, resources = context.engine, context.document, context.resources
    mesh, rest = stages.mesh(context, item.id, options["stage"]), resources.meshes[state.rest].mesh
    goals = tissue_region_goals.resolve(engine, document, resources, item, cancel)
    source = tissue_relaxation.source(engine, document, resources, item)
    query = options["triangle"], options["weights"], stages.frame(context, item, options["stage"])
    rows = native.sample(mesh, rest, source, item, goals, query, cancel)
    return spatial_rows(context, options.get("spatial_target", item.id), rows)


def spatial_rows(context: Any, target: str, rows: Any) -> Any:
    from anthroforge.core.mirroring import parse
    from anthroforge.native.components import transformed

    instance = parse(target)
    if not instance:
        return rows
    frame = context.document.mirrors.plane(context.document.mirrors.instances[target]).frame
    rows = rows.copy()
    rows[:, :3] = transformed(context.engine, rows[:, :3], frame)
    rows[:, 3:6] = transformed(context.engine, rows[:, 3:6], frame)
    return rows


def attach(payload: Any, item: Any, rows: Any) -> None:
    lookup = {region.id: row for region, row in zip(item.constraints, rows, strict=True)}
    for record in payload["report"]["constraints"]:
        row = lookup[record["id"]]
        record.update(goal=row[:3], actual=row[3:6], residual=row[6])
        record["goal_basis"] = (
            "current retained target binding" if record["target"] else "accepted rest"
        )
        payload["lines"].extend((row[:3], row[3:6]))
    payload["report"]["goal_note"] = (
        "World-space goals versus displayed result; "
        "target-relative goals use current accepted targets."
    )
