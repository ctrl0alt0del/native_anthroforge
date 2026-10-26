"""Real pinned remesher exchange and explicit backend failure semantics."""

import sys

import numpy as np
import pytest

from anthroforge.application import quadwild_backend, quadwild_bundle, quadwild_steps
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.skin_guides import Guides
from tests.conftest import CUBE

pytestmark = pytest.mark.skipif(
    sys.platform != "win32" or not quadwild_bundle.location().is_dir(),
    reason="Pinned Windows QuadWild bundle is required",
)


def test_real_guided_backend_retains_quads_and_diagnostics(session, tmp_path):
    mesh = session.engine.import_mesh(CUBE, 1, False)
    guides = Guides(np.empty((0, 10)), np.empty((0, 3)), np.array([0]))
    context = quadwild_steps.Execution(
        session.engine, quadwild_bundle.verify(), NativeCancellation(session.engine)
    )
    folder = tmp_path / "backend work"
    folder.mkdir()
    result = quadwild_backend.run(context, mesh, guides, 64, folder)
    assert result.mesh.counts[1] > 0
    assert np.all(np.diff(result.mesh.array(2)) == 4)
    assert 1 <= len(result.statistics["quantization"]) <= 4
    if any(row["exit_code"] for row in result.statistics["quantization"]):
        assert any("2147483651" in text for text in result.warnings)


def test_bundle_fingerprint_rejects_altered_executable(tmp_path, monkeypatch):
    metadata = dict(platform="Windows", files={"quadwild.exe": "0" * 64})
    monkeypatch.setattr(quadwild_bundle, "manifest", lambda: metadata)
    (tmp_path / "quadwild.exe").write_bytes(b"altered")
    with pytest.raises(ValueError, match="fingerprint"):
        quadwild_bundle.verify(tmp_path)


def test_patch_graph_failure_is_distinct_from_generic_failure(tmp_path):
    log = tmp_path / "trace.log"
    log.write_text("valence not handled: 9")
    with pytest.raises(quadwild_steps.UnsupportedPatchGraph):
        quadwild_steps.check_exit(1, log)
    log.write_text("missing input")
    with pytest.raises(ValueError, match="quantization failed"):
        quadwild_steps.check_exit(1, log)
