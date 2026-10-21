from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.surface_providers import get
from anthroforge.core.construction import Deformer, Target
from anthroforge.core.entities import IDENTITY
from anthroforge.core.shrinkwrap import Shrinkwrap
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.native.shrinkwrap import deform

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"


def cube(session, parent=""):
    result = session.command("import", path=str(CUBE), parent=parent, units=1.0)
    session.wait()
    return result["entity_id"]


def vertices(session, entity):
    return session.assets[session.document.entity(entity).asset].mesh.array(0).copy()


@pytest.mark.parametrize(
    "mode,expected",
    [("ON_SURFACE", 0.4), ("INSIDE", 0.4), ("OUTSIDE", 2), ("OUTSIDE_SURFACE", 0.6)],
)
def test_nearest_modes_preserve_approach_and_weights(session, mode, expected):
    target = cube(session)
    provider = get(session.engine, session.document, session.assets, target)
    binding = Deformer(
        "SHRINKWRAP",
        "",
        Target("probe"),
        weights=(1, 0),
        shrinkwrap=Shrinkwrap(
            SurfaceReference(target), -0.1 if mode == "ON_SURFACE" else 0.1, mode
        ),
    )
    output = deform(session.engine, [[2, 0, 0], [3, 0, 0]], binding, IDENTITY, provider, 0)
    np.testing.assert_allclose(output, [[expected, 0, 0], [3, 0, 0]])


def wrapped_pair(session):
    root = session.command("scp.empty", name="Assembly")
    target = cube(session, root)
    owner = session.command("primitive.create", kind="LOFT", parent=root)
    session.wait()
    binding = session.command("shrinkwrap.add", target={"owner": owner}, surface=target)
    session.wait()
    return target, owner, binding


def test_target_movement_updates_geometry_and_deletion_is_blocked(session):
    target, owner, binding = wrapped_pair(session)
    before = vertices(session, owner)
    session.command("scp.transform", entity=target, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    assert not session.scheduler.errors
    assert session.document.entity(owner).deformers[0].id == binding
    with pytest.raises(ValueError, match="Shrinkwrap"):
        session.command("scp.delete", entity=target)
    assert not np.allclose(before, vertices(session, owner))


def test_shrinkwrap_roundtrip_removal_undo_and_copy(session, tmp_path):
    target, owner, binding = wrapped_pair(session)
    original = session.document
    path = tmp_path / "shrinkwrap.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("open", path=str(path))
    assert session.document.entities == original.entities
    copy = session.command("scp.duplicate", entity=owner)
    assert session.document.entity(copy).deformers[0].shrinkwrap.surface.target == target
    session.command("deformer.remove", binding=binding)
    session.command("undo")
    assert session.document.entity(owner).deformers[0].id == binding
