"""Shared ownership of isolated numerical libraries on a coordinator worker."""

from pathlib import Path
from time import monotonic
from typing import Any

from anthroforge.native import process

from .runtime_launcher import launcher


def arguments(backend: str, source: Path, output: Path, count: int) -> tuple[str, ...]:
    return (*launcher(), "numerical-worker", backend, str(source), str(output), str(count))


def execute(
    engine: Any,
    command: tuple[str, ...],
    folder: Path,
    cancel: Any,
    limits: process.Limits,
    label: str,
) -> dict[str, Any]:
    log = folder / (label + ".log")
    request = process.Request(command, folder, log, limits)
    started = monotonic()
    code = process.run(engine, request, cancel.handle)
    if code:
        raise ValueError(f"{label} failed ({code}); see {log}. Previous output retained.")
    return dict(exit_code=code, elapsed_seconds=monotonic() - started)
