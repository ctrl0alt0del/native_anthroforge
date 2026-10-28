"""Owned numerical measurements; diagnostic values never feed geometry evaluation."""

from typing import Any

import numpy as np

from .mesh import INT64, D, U, doubles, pointer


def configure(engine: Any) -> None:
    engine.bind("af_inspection_metrics", [U, D, D, INT64, D, U])
    engine.bind("af_inspection_section_spans", [U, D, D, D, D, INT64, U])


def measure(mesh: Any, frame: Any, cancel: int = 0) -> dict[str, Any]:
    world = array(frame, 16)
    values, counts, lines = np.zeros(14), np.zeros(5, dtype=np.int64), np.zeros((6, 3))
    mesh.engine.check(
        mesh.engine.library.af_inspection_metrics(
            mesh.handle,
            pointer(world),
            pointer(values),
            counts.ctypes.data_as(INT64),
            pointer(lines),
            cancel,
        )
    )
    return report(values, counts, lines)


def report(values: Any, counts: Any, lines: Any) -> dict[str, Any]:
    return dict(
        bounds=values[:6].tolist(),
        extents=values[6:9].tolist(),
        conditioning=conditioning(values, counts),
        lines=lines.tolist(),
        units="metres",
        axes=["World X", "World Y", "World Z"],
    )


def conditioning(values: Any, counts: Any) -> dict[str, Any]:
    return dict(
        minimum_edge=values[9],
        maximum_edge=values[10],
        minimum_triangle_quality=values[11],
        transform_condition=values[12],
        offset_extent_ratio=values[13],
        edges=int(counts[0]),
        boundary_edges=int(counts[1]),
        nonmanifold_edges=int(counts[2]),
        orientation_conflicts=int(counts[3]),
        degenerate_faces=int(counts[4]),
        containment="Unavailable: this check does not classify enclosed volume.",
        penetration="Unavailable: crossing triangles do not establish penetration depth.",
    )


def section(mesh: Any, frame: Any, plane: Any, cancel: int = 0) -> dict[str, Any]:
    world, equation = array(frame, 16), array(plane, 4)
    values, counts, lines = np.zeros(8), np.zeros(3, dtype=np.int64), np.zeros((4, 3))
    mesh.engine.check(
        mesh.engine.library.af_inspection_section_spans(
            mesh.handle,
            pointer(world),
            pointer(equation),
            pointer(values),
            pointer(lines),
            counts.ctypes.data_as(INT64),
            cancel,
        )
    )
    return section_report(values, counts, lines)


def section_report(values: Any, counts: Any, lines: Any) -> dict[str, Any]:
    return dict(
        spans=values[:2].tolist(),
        axes=values[2:].reshape((2, 3)).tolist(),
        lines=lines.tolist() if counts[0] else [],
        available=bool(counts[0]),
        truncated=bool(counts[2]),
        units="metres",
    )


def array(value: Any, size: int) -> Any:
    result = doubles(value)
    if result.shape != (size,) or not np.isfinite(result).all():
        raise ValueError("Measurement inputs have invalid dimensions or coordinates.")
    return result
