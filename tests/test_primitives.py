from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application.session import Session
from anthroforge.core.construction import Control, Deformer, Target
from anthroforge.core.entities import IDENTITY
from anthroforge.native import construction as native


@pytest.fixture
def studio():
    session = Session()
    yield session
    session.close()


def primitive(session, kind="LOFT", **arguments):
    entity = session.command("primitive.create", kind=kind, **arguments)
    session.command("wait", timeout=5)
    assert not session.scheduler.errors
    return entity


def mesh(session, entity):
    return session.assets[session.document.entity(entity).asset].mesh


def test_loft_has_shared_strips_and_editable_history(studio):
    entity = primitive(studio)
    third = studio.command("curve.add", entity=entity)
    studio.command("wait", timeout=5)
    assert mesh(studio, entity).counts[0] == 96
    assert mesh(studio, entity).counts[1] == 62
    studio.command("undo")
    assert len(studio.document.entity(entity).primitive.curves) == 2
    studio.command("redo")
    assert studio.document.entity(entity).primitive.curves[-1].id == third


@pytest.mark.parametrize("shape", ["BOX", "CYLINDER", "CAPSULE"])
def test_body_shapes_are_native_closed_meshes(studio, shape):
    entity = primitive(studio, "BODY", shape=shape)
    result = mesh(studio, entity)
    faces, offsets = result.array(1), result.array(2)
    edges = []
    for a, b in zip(offsets[:-1], offsets[1:], strict=True):
        face = faces[a:b]
        edges.extend(
            tuple(sorted((int(v), int(face[(i + 1) % len(face)])))) for i, v in enumerate(face)
        )
    assert all(edges.count(edge) == 2 for edge in set(edges))


def test_hook_bind_is_stationary_then_deforms_and_removes(studio):
    entity = primitive(studio)
    before = mesh(studio, entity).array(0).copy()
    control = studio.command("control.create", entity=entity)
    binding = studio.command("deformer.add", control=control, target={"owner": entity})
    studio.command("wait", timeout=5)
    np.testing.assert_allclose(mesh(studio, entity).array(0), before)
    studio.command("control.transform", control=control, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    studio.command("wait", timeout=5)
    np.testing.assert_allclose(mesh(studio, entity).array(0), before + [0, 0, 0.2])
    studio.command("deformer.remove", binding=binding)
    studio.command("wait", timeout=5)
    np.testing.assert_allclose(mesh(studio, entity).array(0), before)
    assert studio.document.control(control)


def test_lattice_follows_pose_without_false_cycle(studio):
    entity = primitive(studio, "BODY", shape="BOX")
    control = studio.command("control.create", kind="LATTICE", entity=entity)
    studio.command("deformer.add", control=control, target={"owner": entity})
    studio.command("lattice.point", control=control, index=7, position=[0.5, 0.5, 1.5])
    studio.command("wait", timeout=5)
    assert not studio.scheduler.errors
    assert mesh(studio, entity).bounds[5] > 0.05


def test_topology_lock_and_manual_surface(studio):
    entity = primitive(studio)
    child = studio.command("scp.empty", parent=entity, name="Dependent")
    studio.command("wait", timeout=5)
    with pytest.raises(ValueError, match="Topology is locked"):
        studio.command("primitive.update", entity=entity, samples=64)
    studio.command("scp.delete", entity=child)
    studio.command("update_mode", entity=entity, mode="MANUAL")
    previous = mesh(studio, entity).handle
    studio.command("primitive.update", entity=entity, samples=64)
    assert mesh(studio, entity).handle == previous
    studio.command("evaluate", entities=[entity])
    studio.command("wait", timeout=5)
    assert mesh(studio, entity).counts[0] == 128


def test_project_roundtrip_retains_definitions_controls_and_results(studio, tmp_path):
    entity = primitive(studio)
    control = studio.command("control.create", kind="LATTICE", entity=entity)
    studio.command("deformer.add", control=control, target={"owner": entity})
    studio.command("thickness.update", entity=entity, thickness=0.02)
    studio.command("wait", timeout=5)
    source = studio.document
    path = tmp_path / "editable.anthroforge"
    studio.command("save", path=str(path), blocked_policy="wait")
    studio.command("open", path=str(path))
    assert studio.document.entities == source.entities
    assert studio.document.controls == source.controls
    assert mesh(studio, entity).counts[0] == 128


@pytest.mark.parametrize("method", ["LINEAR", "CARDINAL", "CATMULL_ROM", "BSPLINE"])
def test_regular_lattice_is_identity_under_nonuniform_frame(studio, method):
    points = native.lattice_grid(studio.engine, (3, 4, 2))
    cage = Control(
        "cage",
        "LATTICE",
        points=tuple(map(tuple, points)),
        resolution=(3, 4, 2),
        interpolation=(method,) * 3,
    )
    binding = Deformer("LATTICE", cage.id, Target("owner"))
    frame = studio.engine.transform([1, 2, 3, 24, 17, 31, 2, 0.3, 5])
    probes = np.array([[0, 0, 0], [5, -10, 0.3], [-0.1, 0.8, 3]])
    actual = native.lattice(studio.engine, probes, cage, binding, IDENTITY, frame, 0)
    np.testing.assert_allclose(actual, probes, atol=1e-12)


def test_native_hook_weight_falloff_and_binding_matrix(studio):
    control = studio.engine.transform([0, 0, 2, 0, 0, 0, 1, 1, 1])
    binding = weighted_hook()
    points = np.array([[0, 0, 0], [0.5, 0, 0], [2, 0, 0]])
    result = native.hook(studio.engine, points, binding, IDENTITY, control, 0)
    np.testing.assert_allclose(result[:, 2], [1, 0.25, 0])
    inverse = replace(binding, invert=True)
    assert native.hook(studio.engine, points, inverse, IDENTITY, control, 0)[0, 2] == 0


def weighted_hook():
    return Deformer(
        "HOOK",
        "hook",
        Target("owner"),
        strength=0.5,
        radius=1,
        falloff="LINEAR",
        weights=(1, 0.5, 1),
    )
