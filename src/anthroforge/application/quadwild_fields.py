"""Prepare native FLOW constraints and feature files for the pinned remesher."""

from pathlib import Path
from typing import Any

import numpy as np

from anthroforge.native import skin_flow
from anthroforge.native.skin_guides import Guides

from . import quadwild_exchange as exchange
from . import remesher_exchange
from .quadwild_steps import Execution


def field(context: Execution, folder: Path, output: Path, guides: Guides) -> tuple[Any, Any]:
    mesh = remesher_exchange.read_mesh(
        context.engine, folder / "mesh_rem.obj", 3, context.cancellation.handle
    )
    prior = exchange.read_field(folder / "mesh_rem.rosy", mesh.counts[3])
    directions, info = skin_flow.solve(mesh, prior, guides.samples, context.cancellation.handle)
    remesher_exchange.write_triangles(output / "mesh.obj", mesh)
    exchange.write_field(output / "mesh.rosy", directions)
    return mesh, info


def selected(context: Execution, mesh: Any, guides: Guides, sparse: bool) -> Any:
    count = len(guides.offsets) - 1
    if not sparse or not count:
        return range(count)
    return skin_flow.select_paths(mesh, guides.points, guides.offsets, context.cancellation.handle)


def routes(context: Execution, mesh: Any, guides: Guides, indices: Any, warnings: list[str]) -> Any:
    edges = []
    for index in indices:
        a, b = guides.offsets[index : index + 2]
        try:
            edges.append(skin_flow.route(mesh, guides.points[a:b], context.cancellation.handle))
        except ValueError as error:
            if context.cancellation.is_set():
                raise
            warnings.append(str(error))
    return np.vstack(edges) if edges else np.empty((0, 2), dtype=np.int32)


def prepare(
    context: Execution,
    folder: Path,
    output: Path,
    guides: Guides,
    warnings: list[str],
    sparse: bool = False,
) -> dict[str, Any]:
    mesh, info = field(context, folder, output, guides)
    indices = selected(context, mesh, guides, sparse)
    edges = routes(context, mesh, guides, indices, warnings)
    rows = skin_flow.features(mesh, edges, context.cancellation.handle)
    exchange.write_features(output / "mesh.sharp", rows)
    return statistics(info, rows, guides, indices)


def statistics(info: Any, rows: Any, guides: Guides, indices: Any) -> dict[str, Any]:
    return dict(
        constrained_faces=int(np.count_nonzero(info[:, 0] > 0)),
        feature_edges=len(rows),
        requested_paths=len(guides.offsets) - 1,
        selected_paths=len(indices),
    )
