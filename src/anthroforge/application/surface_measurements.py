"""Advisory surface measurements share cancellable inspection jobs and accepted inputs."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.scheduling import Workload
from anthroforge.native import inspection_metrics

from . import inspection_surfaces


def surface(context: Any, target: str, options: Any) -> Any:
    return inspection_surfaces.get(context, target, options.get("stage", "final"))


def validate(context: Any, target: str, options: Any) -> None:
    selected = surface(context, target, options)
    selected.mesh(context)
    if options.get("expected_asset", selected.asset) != selected.asset:
        raise ValueError("The surface changed. Wait for its current display and measure again.")
    if "plane" in options:
        inspection_metrics.array(options["plane"], 4)


def signature(context: Any, target: str, options: Any) -> Any:
    validate(context, target, options)
    selected = surface(context, target, options)
    return selected.target, selected.stage, selected.asset, selected.frame, selected.revision


def workload(context: Any, target: str, options: Any) -> Workload:
    return Workload(triangles=surface(context, target, options).mesh(context).counts[3])


def compute(context: Any, target: str, options: Any, cancel: int) -> dict[str, Any]:
    selected = surface(context, target, options)
    mesh = selected.mesh(context)
    measured = inspection_metrics.measure(mesh, selected.frame, cancel)
    if "plane" in options:
        measured["section"] = inspection_metrics.section(
            mesh, selected.frame, options["plane"], cancel
        )
    return dict(report=dict(measured, surface=asdict(selected), revision=context.document.revision))
