"""Native source correspondence survives evaluation, deformation and project persistence."""

import numpy as np
import pytest

from anthroforge.native import construction, material, topology
from tests.test_surface_branches import branched
from tests.test_surface_workflow import curve, surface


def mesh(session, target):
    return session.assets[session.document.object(target).result.asset].mesh


def sources(session):
    return [curve(session, y) for y in (0, 0.4)]


def grids(data):
    result, cursor = [], 0
    while cursor < len(data):
        header = data[cursor : cursor + 5]
        count = int(header[-1])
        result.append((header, data[cursor + 5 : cursor + 5 + count]))
        cursor += 5 + count
    return result


def test_loft_grid_uses_exact_canonical_vertices_and_survives_deformation(session):
    target = surface(session, sources(session))
    original = mesh(session, target)
    data = material.array(original)
    header, indices = grids(data)[0]
    assert header[0] * header[1] == original.counts[0]
    np.testing.assert_array_equal(indices, np.arange(original.counts[0]))
    moved = construction.deformed(original, original.array(0) + [0, 0, 0.5])
    np.testing.assert_array_equal(material.array(moved), data)
    finalized = topology.finalize(moved, original, 0)
    np.testing.assert_array_equal(material.array(finalized), data)


def test_branch_material_grids_share_explicit_seam_vertex_ids_and_roundtrip(session, tmp_path):
    _, target, _ = branched(session)
    data = material.array(mesh(session, target))
    parts = grids(data)
    assert len(parts) == 2
    assert len(set(parts[0][1]) & set(parts[1][1])) == parts[1][0][0]
    location = tmp_path / "material.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    np.testing.assert_array_equal(material.array(mesh(session, target)), data)


@pytest.mark.parametrize("data", [[2], [2, 2, 0, 0, 4, 0], [2, 2, 0, 0, 4, 0, 1, 2, 999999]])
def test_malformed_material_never_mutates_the_accepted_mesh(session, data):
    target = surface(session, sources(session))
    original = mesh(session, target)
    before = material.array(original)
    with pytest.raises(ValueError, match="[Mm]aterial"):
        material.restore(original, data)
    np.testing.assert_array_equal(material.array(original), before)
