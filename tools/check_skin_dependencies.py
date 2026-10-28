"""Executable dependency probes, distinct from production geometry qualification."""

import json
from contextlib import chdir
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

import numpy as np

from anthroforge.native.mesh import GeometryEngine

INSTANT_OPTIONS = dict(
    target_vertex_count=64,
    rosy=4,
    posy=4,
    pure_quad=True,
    deterministic=True,
    smooth_iterations=6,
    align_to_boundaries=True,
)


def source():
    mesh = GeometryEngine().import_mesh(Path("examples/primitives/cube.obj"), 1.0, False)
    return mesh.array(0).copy(), mesh.array(3).copy()


def instant(vertices, faces):
    import pyinstantmeshes

    with TemporaryDirectory(prefix="af-skin-probe-") as folder:
        source, target = Path(folder) / "input.obj", Path(folder) / "output.obj"
        write_source(source, vertices, faces)
        pyinstantmeshes.remesh_file(str(source), str(target), **INSTANT_OPTIONS)
        mesh = GeometryEngine().import_mesh(target, 1.0, False)
        assert np.all(np.diff(mesh.array(2)) == 4)
        return mesh.array(0).copy(), mesh.array(1).reshape(-1, 4).copy()


def write_source(path, vertices, faces):
    with path.open("w") as stream:
        for point in vertices:
            stream.write("v " + " ".join(map(str, point)) + "\n")
        for face in faces:
            stream.write("f " + " ".join(str(int(index) + 1) for index in face) + "\n")


def tetrahedra(vertices, faces):
    from pytetwild import PyfTetWildWrapper

    settings = True, False, 0.05, float(np.ptp(vertices, axis=0).max()) / 8
    controls = 1e-3, 10.0, False, 1, 40, 3, False, False, False
    empty = np.empty((0, 3)), np.empty((0, 4), np.int32), np.empty(0)
    with TemporaryDirectory(prefix="af-tet-probe-") as folder, chdir(folder):
        return PyfTetWildWrapper.tetrahedralize_mesh(
            vertices.astype(np.float64), faces.astype(np.uint32), *settings, *controls, *empty
        )


def probe(name, operation, vertices, faces):
    started = perf_counter()
    points, cells = operation(vertices, faces)
    assert len(points) and len(cells) and np.isfinite(points).all()
    assert cells.ndim == 2 and cells.shape[1] == 4
    assert np.min(cells) >= 0 and np.max(cells) < len(points)
    return dict(
        backend=name, vertices=len(points), cells=len(cells), seconds=perf_counter() - started
    )


def main():
    vertices, faces = source()
    results = [
        probe(name, call, vertices, faces)
        for name, call in (("Instant Meshes 1.0.0", instant), ("PyTetWild 0.4.2", tetrahedra))
    ]
    path = Path("build/skin-040/dependency-probes.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2))
    print(path.read_text())


if __name__ == "__main__":
    main()
