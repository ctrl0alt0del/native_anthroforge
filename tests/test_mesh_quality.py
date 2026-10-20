"""Deformation acceptance distinguishes large bending from lost surface validity."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import construction, mesh_quality


def pair(session):
    points = [(-1, -1, 0), (1, -1, 0), (0, 1, 0), (-0.2, 0, 1), (0.2, 0, 1), (0, 0, 2)]
    return session.engine.create_mesh(points, list(range(6)), [0, 3, 6])


def test_rigid_rotation_is_not_a_fold(session):
    rest = pair(session)
    points = rest.array(0).copy()
    points[:, 1:] *= -1
    result = construction.deformed(rest, points)
    quality = mesh_quality.deformation(rest, result)
    assert quality.normal_rotations == 2 and quality.new_collapses == quality.new_crossings == 0
    mesh_quality.validate(rest, result)


def test_new_crossings_fail_but_unchanged_baseline_is_identified(session):
    rest = pair(session)
    points = rest.array(0).copy()
    points[3:, 2] -= 1.5
    result = construction.deformed(rest, points)
    assert mesh_quality.deformation(rest, result).new_crossings == 1
    with pytest.raises(ValueError, match="self-intersections"):
        mesh_quality.validate(rest, result)
    assert mesh_quality.deformation(result, result).baseline_crossings == 1
    mesh_quality.validate(result, result)


def test_new_collapse_fails_and_changed_topology_is_rejected(session):
    rest = pair(session)
    points = rest.array(0).copy()
    points[1] = points[0]
    result = construction.deformed(rest, points)
    assert mesh_quality.deformation(rest, result).new_collapses == 1
    with pytest.raises(ValueError, match="collapsed faces"):
        mesh_quality.validate(rest, result)
    other = session.engine.create_mesh(rest.array(0)[:3], [0, 1, 2], [0, 3])
    with pytest.raises(ValueError, match="identities"):
        mesh_quality.deformation(rest, other)


def test_coincident_shell_boundary_contact_is_not_a_new_crossing(session):
    path = Path(__file__).parent / "fixtures/tissue/boundary_contact.json"
    values = json.loads(path.read_text())
    rest = session.engine.create_mesh(values["base"], list(range(6)), [0, 3, 6])
    output = construction.deformed(rest, values["output"])
    # Front/back vertices have distinct identities but meet only at a fixed point.
    np.testing.assert_array_equal(output.array(0)[0], output.array(0)[3])
    result = mesh_quality.deformation(rest, output)
    assert result.baseline_crossings == result.new_crossings == result.new_collapses == 0
    mesh_quality.validate(rest, output)
