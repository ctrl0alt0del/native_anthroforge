"""Owned backend execution; optional run limits and a bounded diagnostic tail."""

import ctypes as c
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .mesh import U


@dataclass(frozen=True)
class Limits:
    memory: int = 0
    milliseconds: int = 0
    log_bytes: int = 16 * 1024**2


def configure(engine: Any) -> None:
    engine.bind("af_process_run", [c.c_char_p] * 4 + [U] * 4 + [c.POINTER(c.c_uint32)])


@dataclass(frozen=True)
class Request:
    arguments: tuple[str, ...]
    directory: Path
    log: Path
    limits: Limits = Limits()


def validate(limits: Limits) -> None:
    if not all(type(v) is int and 0 <= v < 2**63 for v in vars(limits).values()):
        raise ValueError("Backend limits must be nonnegative signed 64-bit integers.")
    if not limits.log_bytes:
        raise ValueError("Backend log storage must be positive.")


def encode(request: Request) -> tuple[bytes, ...]:
    args = request.arguments
    if not args or not Path(args[0]).is_absolute():
        raise ValueError("Backend executable must be an absolute path.")
    validate(request.limits)
    paths = str(request.directory.resolve()), str(request.log.resolve())
    text = (args[0], subprocess.list2cmdline(args), *paths)
    if any("\0" in value for value in text):
        raise ValueError("Backend arguments cannot contain NUL.")
    return tuple(value.encode("utf-8") for value in text)


def run(engine: Any, request: Request, cancel: int = 0) -> int:
    limits, result = request.limits, c.c_uint32()
    bounds = limits.memory, limits.milliseconds, limits.log_bytes
    status = engine.library.af_process_run(*encode(request), *bounds, cancel, c.byref(result))
    engine.check(status)
    return int(result.value)
