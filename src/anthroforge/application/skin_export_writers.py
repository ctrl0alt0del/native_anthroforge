"""Extensible skin-only serializers; numerical geometry stays in the native mesh."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, TextIO


def require_running(cancel: Any) -> None:
    if cancel.is_set():
        raise ValueError("Skin export cancelled.")


def vertices(stream: TextIO, mesh: Any, cancel: Any) -> None:
    values = mesh.array(0)
    for start in range(0, len(values), 4096):
        require_running(cancel)
        stream.writelines(
            "v " + " ".join(format(float(x), ".17g") for x in row) + "\n"
            for row in values[start : start + 4096]
        )


def faces(stream: TextIO, mesh: Any, cancel: Any) -> None:
    corners, offsets = mesh.array(1), mesh.array(2)
    for start in range(0, len(offsets) - 1, 4096):
        require_running(cancel)
        stream.writelines(
            "f " + " ".join(str(int(v) + 1) for v in corners[offsets[i] : offsets[i + 1]]) + "\n"
            for i in range(start, min(start + 4096, len(offsets) - 1))
        )


def obj(stream: TextIO, mesh: Any, revision: int, cancel: Any) -> None:
    stream.write(f"# AnthroForge skin; metres; application axes; source revision {revision}\n")
    stream.write("o Skin\n")
    vertices(stream, mesh, cancel)
    faces(stream, mesh, cancel)


WRITERS: dict[str, Callable[..., None]] = {".obj": obj}


def writer(path: Path) -> Callable[..., None]:
    try:
        return WRITERS[path.suffix.lower()]
    except KeyError:
        raise ValueError("Unsupported skin format. Available: " + ", ".join(WRITERS)) from None
