"""Pinned Instant Meshes executes inside the shared bounded native process boundary."""

from pathlib import Path
from time import monotonic
from typing import Any

from anthroforge.native import process
from anthroforge.native.mesh import Mesh, NativeCancellation

from . import remesher_exchange as exchange
from .remeshing_result import Result
from .runtime_launcher import launcher

LIMITS = process.Limits()


def run(
    mesh: Mesh,
    target: int,
    folder: Path,
    cancel: NativeCancellation,
    limits: process.Limits = LIMITS,
) -> Result:
    folder = folder.resolve()
    if target < 1 or any(folder.iterdir()):
        raise ValueError("Instant Meshes needs a positive target and an empty work folder.")
    output, arguments = prepare(mesh, target, folder)
    stats = execute(mesh.engine, arguments, folder, cancel, limits)
    result = exchange.read_mesh(mesh.engine, output, 4, cancel.handle)
    return Result(result, (), dict(backend="INSTANT", process=stats, requested_vertices=target))


def prepare(mesh: Mesh, target: int, folder: Path) -> tuple[Path, tuple[str, ...]]:
    source, output = folder / "source.obj", folder / "result.obj"
    exchange.write_triangles(source, mesh)
    arguments = (*launcher(), "numerical-worker", "instant", str(source), str(output), str(target))
    return output, arguments


def execute(
    engine: Any, arguments: tuple[str, ...], folder: Path, cancel: Any, limits: process.Limits
) -> dict[str, Any]:
    log = folder / "instant.log"
    request = process.Request(arguments, folder, log, limits)
    started = monotonic()
    code = process.run(engine, request, cancel.handle)
    if code:
        raise ValueError(f"Instant Meshes failed ({code}); see {log}. Previous output retained.")
    return dict(exit_code=code, elapsed_seconds=monotonic() - started)
