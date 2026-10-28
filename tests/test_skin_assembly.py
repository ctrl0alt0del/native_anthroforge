"""Complete patch assembly matches addon geometry, provenance and fallback policy."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_stitch
from anthroforge.native.mesh import NativeCancellation
from tools.check_skin_assembly import check, inputs, polygons

DATA = json.loads((Path(__file__).parent / "fixtures/skin/assembly.json").read_text())


@pytest.mark.parametrize("row", DATA["cases"])
def test_assembly_matches_addon_positions_winding_and_labels(session, row):
    result = check(session.engine, row)
    if "error" in row:
        assert "parity" in result["rejection"] and "parity" in result["expected"]
        return
    assert result["error"] == 0
    assert result["connectivity"] and result["regions"] and result["guides"]
    assert bool(result["warning"]) == row["allow_unstitched"]
    for actual, expected in zip(
        result["transitions"], row["expected"]["diagnostics"], strict=False
    ):
        assert ("SPARSE", "STAGED", "CENTERED")[int(actual[0])] == expected["mode"]
        np.testing.assert_allclose(actual[-2:], [expected["aspect_p95"], expected["aspect_max"]])


def test_cancel_is_never_converted_into_an_unstitched_quality_warning(session):
    source, annuli = inputs(session.engine, DATA["cases"][0])
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_stitch.assemble(source, annuli, allow_unstitched=True, cancel=token.handle)


def test_assembly_owns_output_without_mutating_inputs(session):
    source, annuli = inputs(session.engine, DATA["cases"][0])
    points, faces = source.array(0), source.array(1)
    result = skin_stitch.assemble(source, annuli)
    np.testing.assert_array_equal(source.array(0), points)
    np.testing.assert_array_equal(source.array(1), faces)
    del source
    annuli.close()
    assert result.topology.mesh.counts[1] == 342
    assert len(polygons(result.topology.mesh.array(1).reshape(-1, 4))) == 342
