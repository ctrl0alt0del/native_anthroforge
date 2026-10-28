"""Revision-qualified contours over accepted stages; the section never changes anatomy."""

from math import isfinite
from typing import Any

from anthroforge.core.scheduling import Workload
from anthroforge.native import sections

from . import inspection_surfaces
from .inspection_context import scene_signature


def inputs(context: Any, target: str, options: Any) -> list[Any]:
    supplied = options.get("surfaces")
    if supplied is not None:
        return list(supplied)
    names = dict.fromkeys((options["stage"], options.get("reference", options["stage"])))
    return [record(inspection_surfaces.get(context, target, name)) for name in names]


def record(surface: Any) -> dict[str, Any]:
    return dict(owner=surface.target, stage=surface.stage, asset=surface.asset, frame=surface.frame)


def validate(context: Any, target: str, options: Any) -> None:
    inspection_surfaces.get(context, target, options["stage"]).mesh(context)
    plane = options.get("plane", ())
    if len(plane) != 4 or not all(isfinite(float(v)) for v in plane):
        raise ValueError("A section requires four finite plane coefficients.")
    rows = inputs(context, target, options)
    if not 1 <= len(rows) <= 8:
        raise ValueError("A section query supports 1–8 displayed stages.")
    for row in rows:
        validate_surface(context, row)


def validate_surface(context: Any, row: Any) -> None:
    from anthroforge.core.mirroring import source

    if (
        source(row["owner"]) not in context.document.registry.records
        and row["owner"] != inspection_surfaces.skin_id(context.document)
        or row["asset"] not in context.assets
    ):
        raise ValueError("A displayed section input is no longer retained. Wait for publication.")


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    return (
        scene_signature(context.document),
        context.document.skin,
        inputs(context, target, options),
    )


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(
        triangles=sum(
            context.assets[r["asset"]].mesh.counts[3] for r in inputs(context, target, options)
        )
    )


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    rows = []
    for row in inputs(context, target, options):
        mesh = context.assets[row["asset"]].mesh
        result = sections.contours(mesh, row["frame"], options["plane"], cancel)
        rows.append(dict(row, **result))
    return dict(
        report=dict(
            surfaces=rows,
            plane=list(options["plane"]),
            revision=context.document.revision,
            method="Triangle-plane contours",
        )
    )
