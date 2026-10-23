"""Retained base/rest connectivity survives recalculation before inflation and cropping."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.native import topology
from tests.test_tissue_workflow import assembly


def alternate_first_quad(mesh):
    arrays = [mesh.array(index).copy() for index in range(5)]
    face = arrays[1][arrays[2][0] : arrays[2][1]]
    assert len(face) == 4
    rows = np.flatnonzero(arrays[4] == 0)
    shared = set(arrays[3][rows[0]]) & set(arrays[3][rows[1]])
    a, b, c, d = face
    changed = ((a, b, d), (b, c, d)) if shared == {a, c} else ((a, b, c), (a, c, d))
    arrays[3][rows] = changed
    return topology.restore(mesh.engine, arrays)


def retain_alternative(session, target, phase):
    item = session.document.object(target)
    key = getattr(item, phase + "_result").asset
    asset = session.assets[key]
    changed = alternate_first_quad(asset.mesh)
    session.assets[key] = replace(asset, mesh=changed)
    return changed.array(3).copy()


@pytest.mark.parametrize("phase", ("base", "rest"))
def test_tissue_retains_accepted_stage_diagonals_during_recalculation(session, phase):
    _, source, target = assembly(session)
    triangles = retain_alternative(session, target, phase)
    if phase == "base":
        session.command("evaluate", entities=[source])
    else:
        session.command("tissue.inflation", target=target, changes=dict(amount=0.07))
    session.wait()
    item = session.document.object(target)
    assert item.result.status == "ready", item.result.error
    mesh = session.assets[getattr(item, phase + "_result").asset].mesh
    np.testing.assert_array_equal(mesh.array(3), triangles)
