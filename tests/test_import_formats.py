import shutil
import struct
from pathlib import Path

import numpy as np
import pytest


def triangle_ply(binary=False):
    mode = "binary_little_endian" if binary else "ascii"
    header = (
        f"ply\nformat {mode} 1.0\nelement vertex 3\nproperty float x\n"
        "property float y\nproperty float z\nelement face 1\n"
        "property list uchar int vertex_indices\nend_header\n"
    ).encode()
    if not binary:
        return header + b"0 0 0\n2 0 0\n0 3 0\n3 0 1 2\n"
    return header + struct.pack("<9fB3i", 0, 0, 0, 2, 0, 0, 0, 3, 0, 3, 0, 1, 2)


def triangle_stl(binary=False):
    if binary:
        return b"binary triangle".ljust(80, b" ") + struct.pack(
            "<I12fH", 1, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0
        )
    return (
        b"solid test\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\n"
        b"vertex 2 0 0\nvertex 0 3 0\nendloop\nendfacet\nendsolid test\n"
    )


@pytest.mark.parametrize("extension,maker", [("ply", triangle_ply), ("stl", triangle_stl)])
@pytest.mark.parametrize("binary", [False, True])
def test_supported_encodings(session, tmp_path, extension, maker, binary):
    path = tmp_path / f"triangle.{extension}"
    path.write_bytes(maker(binary))
    mesh = session.engine.import_mesh(path, 0.001, False)
    assert mesh.counts[3] == 1
    assert mesh.bounds == pytest.approx((0, 0, 0, 0.002, 0.003, 0))


def test_unicode_obj_and_explicit_axis_conversion(session, tmp_path):
    path = tmp_path / "примитив_é.obj"
    shutil.copy2("examples/primitives/cube.obj", path)
    mesh = session.engine.import_mesh(path, 0.01, True)
    assert mesh.counts[:4] == (8, 6, 24, 12)
    assert mesh.bounds == pytest.approx((-0.005, -0.005, -0.005, 0.005, 0.005, 0.005))


def test_triangulation_preserves_outward_winding(session):
    mesh = session.engine.import_mesh(Path("examples/primitives/cube.obj"), 1, False)
    triangles = mesh.array(0)[mesh.array(3)]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    assert (np.sum(normals * triangles.mean(axis=1), axis=1) > 0).all()


@pytest.mark.parametrize("face", ["1 2 99", "1 2 2", "1 2", "1 2 3 4"])
def test_bad_mesh_never_creates_scp(session, tmp_path, face):
    path = tmp_path / "invalid.obj"
    path.write_text("v 0 0 0\nv 1 1 0\nv 0 1 0\nv 1 0 0\nf " + face)
    session.command("import", path=str(path), units=1)
    session.command("wait")
    assert not session.document.entities
    assert session.scheduler.jobs[-1].state == "failed"
