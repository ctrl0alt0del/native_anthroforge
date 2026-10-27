"""Array-only loading uses the same binary and produces a valid tetrahedral proxy."""

import subprocess
import sys

import numpy as np
import pytest

GEOMETRY = (
    "v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],float);"
    "f=np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]],np.uint32);"
)
NO_VISUALIZATION = "assert not any(k.startswith(('pyvista','vtk','PySide6')) for k in sys.modules)"
BINARY = (
    "import hashlib; from pathlib import Path;"
    "digest=hashlib.sha256(Path(t.load().__file__).read_bytes()).hexdigest();"
)


def capture(path, original):
    setup = "from pytetwild import PyfTetWildWrapper; t.load=lambda: PyfTetWildWrapper;"
    code = (
        "import sys,numpy as np; from anthroforge.native import tetrahedral_extension as t;"
        "from anthroforge.application.tetrahedral_backend import tetrahedra;"
        + (setup if original else "")
        + BINARY
        + GEOMETRY
        + "p,c=tetrahedra(v,f,0.3); np.savez(sys.argv[1],vertices=p,tets=c,digest=digest);"
        + ("" if original else NO_VISUALIZATION)
    )
    subprocess.run(
        [sys.executable, "-c", code, str(path)], cwd=path.parent, check=True, capture_output=True
    )
    with np.load(path) as arrays:
        return arrays["vertices"], arrays["tets"], str(arrays["digest"])


def test_array_extension_matches_package_import_without_visualization(tmp_path):
    expected = capture(tmp_path / "package.npz", True)
    actual = capture(tmp_path / "array.npz", False)
    assert expected[2] == actual[2]
    # Unchanged package calls produce different meshes, even at one thread.
    # Compare required volume/boundary invariants, not nondeterministic cell IDs.
    for points, cells, _ in (expected, actual):
        valid_tetrahedron(points, cells)


def valid_tetrahedron(points, cells):
    assert np.isfinite(points).all() and cells.shape[1] == 4 and len(cells)
    assert cells.min() >= 0 and cells.max() < len(points)
    assert points.min() >= -0.002 and points.sum(axis=1).max() <= 1.002
    corners = points[cells]
    volume = np.abs(np.linalg.det(corners[:, 1:] - corners[:, :1])).sum() / 6
    assert volume == pytest.approx(1 / 6, rel=0.01)
