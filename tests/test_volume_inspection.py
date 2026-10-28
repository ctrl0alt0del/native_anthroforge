"""Qualified volume sampling reports its limits and leaves authored geometry untouched."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection_volume
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE
from tests.test_mesh_replacement import source
from tests.test_spatial_evidence import crossing
from tests.test_surface_query_modes import compound


def scaled(value):
    matrix = np.array(IDENTITY).reshape(4, 4)
    matrix[:3, :3] *= value
    return matrix.ravel()


def test_inside_boundary_outside_and_mirror(session):
    target = source(session)
    mesh = session.assets[session.document.entity(target).result.asset].mesh
    inside = inspection_volume.inspect(mesh, scaled(0.5), mesh, IDENTITY, 0)
    assert inside["available"] and inside["inside"] == 8 and inside["outside"] == 0
    assert inside["maximum_inside_distance"] == pytest.approx(0.25)
    assert len(inside["lines"]) == 2
    boundary = inspection_volume.inspect(mesh, IDENTITY, mesh, IDENTITY, 0)
    assert boundary["boundary"] == 8 and boundary["inside"] == 0
    mirror = inspection_volume.inspect(mesh, scaled(2), mesh, scaled([-1, 1, 1]), 0)
    assert mirror["available"] and mirror["outside"] == 8


def test_ambiguous_volumes_and_cancellation_are_explicit(session, tmp_path):
    cube = crossing(session, tmp_path)
    open_id = cube
    cube = session.command("import", path=str(CUBE), parent=cube, units=1)["entity_id"]
    session.wait()
    mesh = session.assets[session.document.entity(cube).result.asset].mesh
    open_mesh = session.assets[session.document.entity(open_id).result.asset].mesh
    result = inspection_volume.inspect(mesh, IDENTITY, open_mesh, IDENTITY, 0)
    assert not result["available"] and result["reason"]
    nested = inspection_volume.inspect(mesh, IDENTITY, compound(session.engine), IDENTITY, 0)
    assert not nested["available"] and nested["reason"] == "Nested interior shells"
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        inspection_volume.inspect(mesh, IDENTITY, mesh, IDENTITY, cancel.handle)


def test_volume_query_is_explicit_read_only_and_revision_qualified(session):
    first = source(session)
    second = session.command("import", path=str(CUBE), parent=first, units=1)["entity_id"]
    session.wait()
    before, cursor = session.document, session.history.cursor
    session.command("geometry.volume", target=first, other=second)
    session.wait()
    result = session.command("geometry.volume.status")
    assert result["state"] == "ready", result
    assert result["report"]["boundary"] == 8
    assert session.document is before and session.history.cursor == cursor
    session.command("scp.delete", entity=second)
    assert session.command("geometry.volume.status")["state"] == "stale"
