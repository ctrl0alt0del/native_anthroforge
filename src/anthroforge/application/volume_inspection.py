"""Explicit two-surface volume diagnosis, independent of geometry production and placement."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.scheduling import Workload
from anthroforge.native import inspection_volume

from . import inspection_surfaces


def inputs(context: Any, target: str, options: Any) -> Any:
    first = inspection_surfaces.get(context, target, options.get("stage", "final"))
    other = inspection_surfaces.get(context, options["other"], options.get("other_stage", "final"))
    return first, other


def validate(context: Any, target: str, options: Any) -> None:
    for surface in inputs(context, target, options):
        surface.mesh(context)


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    return tuple(
        (s.target, s.stage, s.asset, s.frame, s.revision) for s in inputs(context, target, options)
    )


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(
        triangles=sum(s.mesh(context).counts[3] for s in inputs(context, target, options))
    )


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    first, other = inputs(context, target, options)
    result = inspection_volume.inspect(
        first.mesh(context), first.frame, other.mesh(context), other.frame, cancel
    )
    return dict(
        report=dict(
            result, surface=asdict(first), volume=asdict(other), revision=context.document.revision
        )
    )
