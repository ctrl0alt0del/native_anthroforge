"""Native material maps survive result replacement and selected-revision storage."""

import numpy as np
import pytest

from anthroforge.native import construction, tissue_domain, topology
from tests.test_tissue_workflow import assembly, roundtrip


def output(session, key):
    item = session.document.object(key)
    return session.assets[item.rest_result.asset].mesh


def test_material_map_survives_deformation_and_roundtrip(session, tmp_path):
    _, _, key = assembly(session)
    mesh = output(session, key)
    data, weights = tissue_domain.arrays(mesh)
    assert data[1] == 4 and data[2] == mesh.counts[0]
    moved = construction.deformed(mesh, mesh.array(0) + [0, 0, 0.5])
    staged = topology.finalize(moved, mesh, 0)
    np.testing.assert_array_equal(tissue_domain.arrays(staged)[0], data)
    roundtrip(session, tmp_path / "material.anthroforge")
    restored = tissue_domain.arrays(output(session, key))
    np.testing.assert_array_equal(restored[0], data)
    np.testing.assert_array_equal(restored[1], weights)


@pytest.mark.parametrize("fault", ["header", "index", "weight", "size"])
def test_corrupt_material_map_is_rejected_without_mutation(session, fault):
    _, _, key = assembly(session)
    mesh = output(session, key)
    data, weights = tissue_domain.arrays(mesh)
    original = data.copy()
    if fault == "weight":
        weights[0] = -1
    elif fault == "index":
        data[9 + mesh.counts[0]] = -1
    else:
        data[0 if fault == "header" else 5] = -1
    with pytest.raises(ValueError, match="[Tt]issue"):
        tissue_domain.restore(mesh, data, weights)
    np.testing.assert_array_equal(tissue_domain.arrays(mesh)[0], original)
