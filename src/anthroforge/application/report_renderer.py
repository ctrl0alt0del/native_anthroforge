"""Isolated optional desktop renderer; the headless process never imports Qt."""

import os
import subprocess
import sys
from pathlib import Path
from threading import Event
from time import monotonic
from typing import BinaryIO


def command(root: Path, revision: int) -> list[str]:
    packaged = "__compiled__" in globals()  # Nuitka's documented runtime module marker.
    entry = [sys.executable, "--cli"] if packaged else [sys.executable, "-m", "anthroforge"]
    return [
        *entry,
        "render",
        str(root / "snapshot.anthroforge"),
        str(root / "image.png"),
        "--revision",
        str(revision),
        "--view",
        str(root / "view.json"),
    ]


def render(root: Path, revision: int, cancel: Event) -> None:
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    with (root / "renderer.log").open("w+b") as log:
        with subprocess.Popen(
            command(root, revision), stdout=log, stderr=log, creationflags=flags
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
