"""Isolated optional desktop renderer; the headless process never imports Qt."""

import subprocess
import sys
from pathlib import Path
from threading import Event
from time import monotonic
from typing import BinaryIO

from .runtime_launcher import launcher

if sys.platform == "win32":
    CREATION_FLAGS = subprocess.CREATE_NO_WINDOW
else:
    CREATION_FLAGS = 0


def command(root: Path, revision: int) -> list[str]:
    return [
        *launcher(),
        "render",
        str(root / "snapshot.anthroforge"),
        str(root / "image.png"),
        "--revision",
        str(revision),
        "--view",
        str(root / "view.json"),
    ]


def render(root: Path, revision: int, cancel: Event) -> None:
    execute(root, command(root, revision), cancel)


def render_scene(root: Path, cancel: Event) -> None:
    execute(root, [*launcher(), "render-inspection", str(root), str(root / "image.png")], cancel)


def execute(root: Path, arguments: list[str], cancel: Event) -> None:
    with (root / "renderer.log").open("w+b") as log:
        with subprocess.Popen(
            arguments, stdout=log, stderr=log, creationflags=CREATION_FLAGS
        ) as process:
            try:
                wait(process, cancel)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
            if process.returncode:
                failure(log)


def failure(log: BinaryIO) -> None:
    log.seek(0)
    raise ValueError("Inspection renderer failed: " + log.read(8192).decode(errors="replace"))


def wait(process: subprocess.Popen[bytes], cancel: Event) -> None:
    deadline = monotonic() + 120
    while process.poll() is None:
        if cancel.is_set() or monotonic() > deadline:
            raise ValueError("Inspection renderer cancelled or timed out.")
        try:
            process.wait(timeout=0.1)
        except subprocess.TimeoutExpired:
            continue
