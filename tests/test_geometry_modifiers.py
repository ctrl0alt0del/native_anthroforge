import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import geometry_modifiers, triangle_material
from tests.test_segment_chain import REFERENCE, source_settings
from tests.test_segment_material import construct, matching_triangle, records
from tests.test_shrinkwrap import cube, vertices


def source_mesh(engine, record):
    faces = record["faces"]
    return engine.create_mesh(
        record["vertices"], [i for f in faces for i in f], np.cumsum([0, *map(len, faces)])
    )


def test_simple_subdivision_matches_blender(session):
    data = json.loads(
        (Path(__file__).parent / "fixtures/primitives/blender501_simple.json").read_text()
    )
    base = source_mesh(session.engine, data["source"])
    result = geometry_modifiers.subdivide(base, 2)
    expected = np.asarray(data["subdivided"]["vertices"])
    actual = result.array(0)
    distance = np.linalg.norm(actual[:, None, :] - expected[None, :, :], axis=2)
    assert actual.shape == expected.shape
    assert max(distance.min(axis=0).max(), distance.min(axis=1).max()) < 2e-6


def test_ordered_geometry_stages_persist_and_lock_topology(session, tmp_path):
    entity = cube(session)
    subdiv = session.command("modifier.add", entity=entity, kind="SUBDIVISION", levels=2)
    session.command("modifier.add", entity=entity, kind="DISPLACE", offset=[0, 0, -6.6])
    session.wait()
    assert not session.scheduler.errors
    np.testing.assert_allclose(vertices(session, entity).mean(axis=0), [0, 0, -6.6], atol=1e-8)
    session.command("scp.empty", parent=entity, name="Child")
    with pytest.raises(ValueError, match="Topology"):
        session.command("modifier.update", binding=subdiv, levels=3)
    path = tmp_path / "modifiers.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("open", path=str(path))
    assert session.document.entity(entity).deformers[0].subdivision == 2


def test_union_provenance_survives_simple_refinement(session):
    from dataclasses import replace

    from anthroforge.core.entities import IDENTITY
    from anthroforge.native import material_bindings

    mesh = construct(session.engine, replace(source_settings(REFERENCE["cases"][1]), unite=True), 0)
    refined = geometry_modifiers.subdivide(mesh, 2)
    triangle, _, _ = matching_triangle(mesh)
    before = material_bindings.frames(mesh, mesh, IDENTITY, records(mesh, triangle))
    after = material_bindings.frames(mesh, refined, IDENTITY, records(mesh, triangle))
    np.testing.assert_allclose(before, after, atol=1e-7)
    assert triangle_material.arrays(refined)[0].size > triangle_material.arrays(mesh)[0].size
