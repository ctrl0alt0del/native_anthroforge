"""Generated-output import preserves the established tessellation and validation boundary."""

import numpy as np
import pytest

from anthroforge.application import remesher_exchange


def source(tmp_path, face):
    path = tmp_path / "result.obj"
    path.write_text("v 0 0 0\nv 1 1 0\nv 0 1 0\nv 1 0 0\n" + face + "\n", encoding="utf-8")
    return path


def test_generated_folded_quad_retains_vertices_and_polygon(session, tmp_path):
    path = source(tmp_path, "f 1 2 3 4")
    with pytest.raises(ValueError):
        session.engine.import_mesh(path, 1, False)
    mesh = remesher_exchange.read_mesh(session.engine, path, 4, 0)
    np.testing.assert_array_equal(mesh.array(0), [[0, 0, 0], [1, 1, 0], [0, 1, 0], [1, 0, 0]])
    np.testing.assert_array_equal(mesh.array(1), [0, 1, 2, 3])
    assert mesh.counts[3] == 2


@pytest.mark.parametrize("face", ["f 1 2 3", "f 1 1 2 4", "f 1 2 3 99"])
def test_malformed_quad_is_not_silently_repaired(session, tmp_path, face):
    with pytest.raises(ValueError):
        remesher_exchange.read_mesh(session.engine, source(tmp_path, face), 4, 0)
