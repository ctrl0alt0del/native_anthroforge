"""Backend policy over shared native preparation, refinement and patch assembly."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from anthroforge.native import (
    skin_annuli,
    skin_density,
    skin_proxy,
    skin_stitch,
    skin_symmetry,
    skin_topology,
)

from . import instant_backend, quadwild_backend, quadwild_bundle, quadwild_steps, worker_memory


@dataclass(frozen=True)
class Inputs:
    envelope: Any
    annuli: Any
    density: Any
    guides: Any
    plane: Any
    settings: Any


def initial_target(inputs: Inputs, cancel: Any) -> int:
    reserved = 3 * int(inputs.annuli.counts[1])
    target = int(inputs.settings.target_quads)
    if inputs.density.adaptive:
        target = skin_density.base_count(
            inputs.envelope, inputs.density.density.lengths, target, reserved, cancel.handle
        )
    if inputs.settings.backend == "INSTANT":
        return max(128, round(max(512, target - reserved) / 9.0))
    return max(128, target - reserved)


def prepare(inputs: Inputs, cancel: Any) -> Any:
    target = min(300000, max(64000, 2 * inputs.settings.target_quads))
    proxy = skin_proxy.decimate(inputs.envelope, target, worker_memory.budget(), cancel.handle)
    proxy = skin_density.smooth_proxy(proxy, cancel=cancel.handle)
    if inputs.plane is not None:
        proxy = skin_symmetry.half(proxy, inputs.plane, cancel.handle)
    return skin_annuli.cut_guides(proxy, inputs.annuli, inputs.plane, cancel.handle)


def backend(inputs: Inputs, proxy: Any, target: int, cancel: Any, folder: Path) -> Any:
    if inputs.settings.backend == "INSTANT":
        return instant_backend.run(proxy, target, folder, cancel)
    context = quadwild_steps.Execution(proxy.engine, quadwild_bundle.verify(), cancel)
    guides = inputs.guides
    if inputs.plane is not None:
        guides = skin_symmetry.guides(proxy.engine, guides, inputs.plane, cancel.handle)
        target = max(64, round(target / 2))
    return quadwild_backend.run(context, proxy, guides, target, folder)


def assemble(inputs: Inputs, mesh: Any, cancel: Any) -> Any:
    if inputs.plane is not None:
        mesh = skin_symmetry.mirror(mesh, inputs.plane, cancel.handle).mesh
    if inputs.density.adaptive:
        mesh = skin_topology.refine(
            mesh,
            inputs.envelope,
            inputs.density.density.lengths,
            inputs.settings.target_quads,
            plane=inputs.plane,
            cancel=cancel.handle,
        ).mesh
    return skin_stitch.assemble(
        mesh, inputs.annuli, inputs.plane, inputs.settings.backend == "QUADWILD", cancel.handle
    )


def attempt(inputs: Inputs, proxy: Any, target: int, cancel: Any) -> tuple[Any, Any]:
    with TemporaryDirectory(prefix="anthroforge-topology-") as directory:
        folder = Path(directory)
        try:
            result = backend(inputs, proxy, target, cancel, folder)
            return assemble(inputs, result.mesh, cancel), result
        except ValueError as error:
            detail = failure_logs(folder)
            raise ValueError(f"{error}\n{detail}" if detail else str(error)) from error


def failure_logs(folder: Path) -> str:
    logs = sorted(folder.rglob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        return ""
    with logs[0].open("rb") as stream:
        stream.seek(max(0, logs[0].stat().st_size - 3000))
        return stream.read().decode("utf-8", errors="replace")


def run(inputs: Inputs, cancel: Any) -> tuple[Any, Any, list[Any]]:
    proxy, target = prepare(inputs, cancel), initial_target(inputs, cancel)
    assembled, result = attempt(inputs, proxy, target, cancel)
    attempts = [result.statistics | dict(internal_target=target)]
    wanted, actual = inputs.settings.target_quads, assembled.topology.mesh.counts[1]
    if inputs.settings.backend == "INSTANT" and abs(actual - wanted) > 0.15 * max(1, wanted):
        target = max(128, round(target * wanted / max(1, actual)))
        assembled, result = attempt(inputs, proxy, target, cancel)
        attempts.append(result.statistics | dict(internal_target=target))
    return assembled, result, attempts
