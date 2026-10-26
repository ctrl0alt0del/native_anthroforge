"""Reference-only proxy building is bounded and does not initialize Qt."""

import sys

import numpy as np
import pytest

from anthroforge.application import tetrahedral_backend
from anthroforge.native import process
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Bounded Windows worker")


def test_isolated_proxy_preserves_source_and_owns_output(session, tmp_path):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    before = mesh.array(0).copy()
    result = tetrahedral_backend.run(mesh, 8, tmp_path, NativeCancellation(session.engine))
    points, cells = result.arrays["proxy_vertices"], result.arrays["proxy_tets"]
    assert cells.shape[1] == 4 and len(cells) and not points.flags.writeable
    assert np.max(np.abs(points)) <= 0.501
    np.testing.assert_array_equal(mesh.array(0), before)


def test_proxy_cancellation_does_not_publish_a_partial_result(session, tmp_path):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        tetrahedral_backend.run(mesh, 8, tmp_path, token)


def test_proxy_output_budget_checked_before_loading(tmp_path):
    path = tmp_path / "proxy.npz"
    np.savez_compressed(path, vertices=np.zeros((1000, 3)), tets=np.zeros((1000, 4), np.int32))
    with pytest.raises(ValueError, match="budget"):
        tetrahedral_backend.read(path, process.Limits().log_bytes // 1000, {})
