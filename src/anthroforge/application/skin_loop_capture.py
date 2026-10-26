"""Closed Fiber guides retain accepted-path identities, including reflected instances."""

from dataclasses import dataclass
from typing import Any

from anthroforge.core import skin_sources
from anthroforge.native import skin_loops

from . import skin_capture


@dataclass(frozen=True)
class Capture:
    sources: tuple[skin_capture.Source, ...]
    data: skin_loops.Loops
    warnings: tuple[str, ...]


def sources(engine: Any, document: Any, resources: Any, cancel: Any) -> tuple[Any, Any]:
    rows: list[skin_capture.Source] = []
    warnings: list[str] = []
    for source in skin_sources.candidates(document):
        if source.kind != "FIBER":
            continue
        append(engine, document, resources, source, cancel, rows, warnings)
    return tuple(rows), warnings


def append(
    engine: Any, document: Any, resources: Any, source: Any, cancel: Any, rows: Any, warnings: Any
) -> None:
    try:
        if cancel.is_set():
            raise ValueError("Skin loop capture cancelled.")
        accepted = skin_capture.fiber(engine, document, resources, source, cancel.handle)
        if accepted.mesh.closed:
            rows.append(accepted)
    except (KeyError, ValueError) as error:
        if cancel.is_set():
            raise
        if document.object(source.owner).closed:
            warnings.append(f"Loop unavailable for {document.object(source.owner).name}: {error}")


def capture(
    engine: Any, document: Any, resources: Any, mesh: Any, cancel: Any, plane: Any = None
) -> Capture:
    rows, warnings = sources(engine, document, resources, cancel)
    data = skin_loops.prepare(
        mesh, [row.mesh for row in rows], [row.frame for row in rows], plane, cancel.handle
    )
    for row, status in zip(rows, data.statuses, strict=True):
        if status in (1, 3):
            name = document.object(row.identity.owner).name
            reason = "unpaired" if status == 1 else "zero projected perimeter"
            warnings.append(
                f"Ignored topology loop {name} ({row.identity.instance or 'source'}): {reason}."
            )
    return Capture(rows, data, tuple(warnings))
