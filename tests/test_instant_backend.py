"""Real isolated remeshing, cancellation, errors and absence of GUI initialization."""

import sys

import numpy as np
import pytest

from anthroforge.application import instant_backend
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Bounded Windows worker")


def test_real_instant_backend_is_repeatable_and_pure_quad(session, tmp_path):
    source = session.engine.import_mesh(CUBE, 1, False)
    token = NativeCancellation(session.engine)
    first = tmp_path / "first run"
    second = tmp_path / "second run"
    first.mkdir()
    second.mkdir()
    a = instant_backend.run(source, 64, first, token)
    b = instant_backend.run(source, 64, second, token)
    np.testing.assert_array_equal(a.mesh.array(0), b.mesh.array(0))
    np.testing.assert_array_equal(a.mesh.array(1), b.mesh.array(1))
    assert a.mesh.counts[1] and np.all(np.diff(a.mesh.array(2)) == 4)
    assert a.statistics["process"]["exit_code"] == 0 and not a.warnings


def test_instant_cancel_does_not_return_a_successful_mesh(session, tmp_path):
    token = NativeCancellation(session.engine)
    token.set()
    source = session.engine.import_mesh(CUBE, 1, False)
    with pytest.raises(ValueError, match="[Cc]ancel"):
        instant_backend.run(source, 64, tmp_path, token)
