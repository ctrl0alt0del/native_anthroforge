"""Surface-distance samples do not masquerade as corresponding material displacement."""

import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native.comparison import distances
from tests.conftest import CUBE


def test_material_displacement_and_geometric_samples_are_distinct(session):
    engine = session.engine
    mesh = engine.import_mesh(CUBE, 1, False)
    shifted = engine.transform([0.5, 0, 0, 0, 0, 0, 1, 1, 1])
    result = distances(mesh, IDENTITY, mesh, shifted, True)
    assert result["material"]["mean"] == pytest.approx(0.5)
    assert result["material"]["samples"] == mesh.counts[0]
    assert result["geometric"]["minimum"] < result["material"]["minimum"]
    assert distances(mesh, IDENTITY, mesh, shifted, False)["material"] is None


def test_reordered_connectivity_cannot_claim_material_displacement(session):
    engine = session.engine
    mesh = engine.import_mesh(CUBE, 1, False)
    other = engine.create_mesh(mesh.array(0), mesh.array(1)[::-1].copy(), mesh.array(2))
    with pytest.raises(ValueError, match="correspondence|connectivity"):
        distances(mesh, IDENTITY, other, IDENTITY, True)
