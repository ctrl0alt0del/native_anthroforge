"""QuadWild FLOW pipeline; topology assembly and document publication are separate owners."""

from pathlib import Path
from typing import Any

from anthroforge.native import skin_flow
from anthroforge.native.mesh import Mesh
from anthroforge.native.skin_guides import Guides

from . import quadwild_fields, quadwild_steps
from . import remesher_exchange as exchange
from .quadwild_steps import Execution, UnsupportedPatchGraph
from .remeshing_result import Result


def calibrate(
    context: Execution, folder: Path, target: int, warnings: list[str]
) -> tuple[Any, Any]:
    state, best, records = (1.0, float("inf")), None, []
    for attempt in range(4):
        mesh, stats = quadwild_steps.quantize(context, folder, state[0], attempt)
        records.append(stats | dict(scale=float(state[0]), quads=mesh.counts[1]))
        report_exit(stats, warnings)
        state, flags = skin_flow.calibration_step(context.engine, target, mesh.counts[1], state)
        if flags & 1:
            best = state[1], mesh
        if flags & 2:
            break
    return best, records


def guided(
    context: Execution, source: Path, output: Path, guides: Guides, target: int, warnings: list[str]
) -> tuple[Any, Any, Any, Any]:
    field = quadwild_fields.prepare(context, source, output, guides, warnings)
    tracing = quadwild_steps.trace(context, output, True)
    try:
        best, attempts = calibrate(context, output, target, warnings)
    except UnsupportedPatchGraph:
        (output / "trace.log").replace(output / "trace.initial.log")
        field = quadwild_fields.prepare(context, source, output, guides, warnings, True)
        tracing = quadwild_steps.trace(context, output, True) | dict(initial=tracing)
        report_retry(field, warnings)
        best, attempts = calibrate(context, output, target, warnings)
    return best, attempts, field, tracing


def report_warnings(best: Any, target: int, tracing: Any, warnings: list[str]) -> None:
    if best[0] > 0.15 * target:
        warnings.append(
            f"QuadWild achieved {best[1].counts[1]} quads for requested {target}; "
            "patch constraints limit density."
        )
    if tracing["discarded_patches"]:
        warnings.append(
            f"QuadWild discarded {tracing['discarded_patches']} invalid patches; "
            "inspect coverage and openings."
        )


def run(context: Execution, mesh: Mesh, guides: Guides, target: int, folder: Path) -> Result:
    if target < 1 or any(folder.iterdir()):
        raise ValueError("QuadWild needs a positive target and an empty dedicated work folder.")
    warnings: list[str] = []
    exchange.write_triangles(folder / "mesh.obj", mesh)
    baseline = quadwild_steps.trace(context, folder)
    output = folder / "guided"
    output.mkdir()
    best, attempts, field, tracing = guided(
        context, folder, output, guides, max(64, target), warnings
    )
    report_warnings(best, max(64, target), tracing, warnings)
    return result(best[1], warnings, baseline, tracing, field, attempts)


def report_exit(stats: Any, warnings: list[str]) -> None:
    if stats["exit_code"]:
        warnings.append("QuadWild produced validated output but exited abnormally (2147483651).")


def report_retry(field: Any, warnings: list[str]) -> None:
    warnings.append(
        f"Retried rejected patch graph with {field['selected_paths']}/{field['requested_paths']} "
        "separated paths; all directions retained."
    )


def result(
    mesh: Mesh, warnings: list[str], baseline: Any, tracing: Any, field: Any, attempts: Any
) -> Result:
    statistics = dict(
        backend="QUADWILD",
        field=field,
        automatic_trace=baseline,
        guided_trace=tracing,
        quantization=attempts,
    )
    return Result(mesh, tuple(dict.fromkeys(warnings)), statistics)
