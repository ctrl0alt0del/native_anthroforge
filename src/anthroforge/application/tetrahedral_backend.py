"""Owned proxy preparation; fTetWild cannot outlive its coordinator job."""

from pathlib import Path
from typing import Any
from zipfile import ZipFile

import numpy as np

from anthroforge.native import process

from . import numerical_process, skin_assets

LIMITS = process.Limits()


def run(
    mesh: Any, resolution: int, folder: Path, cancel: Any, limits: process.Limits = LIMITS
) -> skin_assets.SkinAsset:
    folder = folder.resolve()
    if type(resolution) is not int or not 8 <= resolution <= 256 or any(folder.iterdir()):
        raise ValueError("Proxy preparation requires resolution 8–256 and an empty folder.")
    source, output = folder / "source.npz", folder / "proxy.npz"
    extent = max(mesh.bounds[i + 3] - mesh.bounds[i] for i in range(3))
    np.savez(source, vertices=mesh.array(0), faces=mesh.array(3), length=extent / resolution)
    command = numerical_process.arguments("tetrahedral", source, output, resolution)
    stats = numerical_process.execute(mesh.engine, command, folder, cancel, limits, "tetrahedral")
    return read(output, limits.memory, dict(backend="pytetwild-0.4.2", process=stats))


def read(path: Path, budget: int, metadata: dict[str, Any]) -> skin_assets.SkinAsset:
    with ZipFile(path) as archive:
        if budget and sum(item.file_size for item in archive.infolist()) > budget:
            raise ValueError("Tetrahedral proxy output exceeds its memory budget.")
    with np.load(path, allow_pickle=False) as data:
        vertices, cells = data["vertices"], data["tets"]
        validate(vertices, cells)
        return skin_assets.create(dict(proxy_vertices=vertices, proxy_tets=cells), metadata)


def validate(vertices: Any, cells: Any) -> None:
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not len(vertices):
        raise ValueError("Tetrahedral proxy requires XYZ vertices.")
    if cells.ndim != 2 or cells.shape[1] != 4 or not len(cells) or cells.dtype.kind not in "iu":
        raise ValueError("Tetrahedral proxy requires nonempty integer tetrahedra.")
    if not np.isfinite(vertices).all() or cells.min() < 0 or cells.max() >= len(vertices):
        raise ValueError("Tetrahedral proxy contains invalid vertices or indices.")


def worker(source: Path, output: Path, resolution: int) -> None:
    if not 8 <= resolution <= 256:
        raise ValueError("Proxy resolution must be between 8 and 256.")
    with np.load(source, allow_pickle=False) as data:
        vertices, faces = data["vertices"], np.ascontiguousarray(data["faces"], dtype=np.uint32)
        points, cells = tetrahedra(vertices, faces, float(data["length"]))
    validate(points, cells)
    np.savez(output, vertices=points, tets=cells)


def tetrahedra(vertices: Any, faces: Any, length: float) -> Any:
    from pytetwild import PyfTetWildWrapper

    # The pinned nanobind function is positional-only; its named stub differs.
    native: Any = PyfTetWildWrapper.tetrahedralize_mesh
    settings = True, False, 0.05, length
    controls = 1e-3, 10.0, False, 4, 40, 3, False, False, False
    empty = np.empty((0, 3)), np.empty((0, 4), np.int32), np.empty(0)
    return native(vertices, faces, *settings, *controls, *empty)
