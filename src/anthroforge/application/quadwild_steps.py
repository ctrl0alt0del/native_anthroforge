"""Pinned QuadWild process stages; nonzero usable-output cases remain explicit."""

import re
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any

from anthroforge.native import process
from anthroforge.native.mesh import GeometryEngine, NativeCancellation

from . import quadwild_exchange as exchange


class UnsupportedPatchGraph(ValueError):
    pass


@dataclass(frozen=True)
class Execution:
    engine: GeometryEngine
    vendor: Path
    cancellation: NativeCancellation
    limits: process.Limits = process.Limits()

    def run(self, folder: Path, arguments: tuple[str, ...], label: str) -> dict[str, Any]:
        started = monotonic()
        request = process.Request(arguments, self.vendor, folder / f"{label}.log", self.limits)
        code = process.run(self.engine, request, self.cancellation.handle)
        return dict(exit_code=code, elapsed_seconds=monotonic() - started)


def trace(context: Execution, folder: Path, guided: bool = False) -> dict[str, Any]:
    args = trace_arguments(context, folder, guided)
    stats = context.run(folder, tuple(map(str, args)), "trace")
    if stats["exit_code"]:
        raise ValueError(
            f"QuadWild tracing failed: {stats['exit_code']}; see {folder / 'trace.log'}"
        )
    erased = re.findall(
        r"(\d+)- NON DISK OR NON MANIF PATCH ERASED", (folder / "trace.log").read_text()
    )
    return stats | dict(discarded_patches=max(map(int, erased), default=0))


def quantize(context: Execution, folder: Path, scale: float, index: int) -> tuple[Any, Any]:
    config = folder / f"quantize_{index}.txt"
    original = (context.vendor / "config/main_config/flow.txt").read_text()
    config.write_text(original.replace("scaleFact 1", f"scaleFact {scale:.9g}"))
    output = folder / "mesh_rem_p0_1_quadrangulation_smooth.obj"
    output.unlink(missing_ok=True)
    args = (context.vendor / "quad_from_patches.exe", folder / "mesh_rem_p0.obj", 1, config)
    stats = context.run(folder, tuple(map(str, args)), f"quantize_{index}")
    check_exit(stats["exit_code"], folder / f"quantize_{index}.log")
    mesh = exchange.read_mesh(context.engine, output, 4, context.cancellation.handle)
    return mesh, stats


def check_exit(code: int, log: Path) -> None:
    if code in (0, 2147483651):
        return
    if "valence not handled:" in log.read_text(errors="replace"):
        raise UnsupportedPatchGraph("Bi-MDF cannot quantize the traced patch valence.")
    raise ValueError(f"QuadWild quantization failed: {code}; see {log}")


def trace_arguments(context: Execution, folder: Path, guided: bool) -> list[Any]:
    settings = folder / "prep.txt"
    settings.write_text("do_remesh 0\nsharp_feature_thr -1\nalpha 0.02\nscaleFact 1\n")
    args = [context.vendor / "quadwild.exe", folder / "mesh.obj", 2, settings]
    if guided:
        args.append(folder / "mesh.rosy")
    if (folder / "mesh.sharp").exists():
        args.append(folder / "mesh.sharp")
    return args
