"""Pinned Instant Meshes executes inside the shared bounded native process boundary."""

from pathlib import Path

from anthroforge.native import process
from anthroforge.native.mesh import Mesh, NativeCancellation

from . import numerical_process
from . import remesher_exchange as exchange
from .remeshing_result import Result

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
    stats = numerical_process.execute(mesh.engine, arguments, folder, cancel, limits, "instant")
    result = exchange.read_mesh(mesh.engine, output, 4, cancel.handle)
    return Result(result, (), dict(backend="INSTANT", process=stats, requested_vertices=target))


def prepare(mesh: Mesh, target: int, folder: Path) -> tuple[Path, tuple[str, ...]]:
    source, output = folder / "source.obj", folder / "result.obj"
    exchange.write_triangles(source, mesh)
    arguments = numerical_process.arguments("instant", source, output, target)
    return output, arguments
