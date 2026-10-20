"""Shared construction lifecycle through the public, renderer-independent API."""

import json
import zipfile
from threading import Event
from time import monotonic

import numpy as np
import pytest

from anthroforge.application import construction_tasks, storage
from anthroforge.application.control_frames import display_frame
from anthroforge.application.task_schedulers import MeasuredTaskScheduler
from anthroforge.native import components
from anthroforge.native.scene import entity_frame
from tests.test_construction_contracts import create, hook, lift_first_point, mesh, move_control


def test_pose_edit_during_first_construction_preserves_geometry_job(session):
    entity = session.command("primitive.create", kind="BODY")
    job = next(j for j in session.scheduler.jobs if j.kind == "construction")
    assert session.document.entity(entity).result.status == "pending"
    session.command("scp.transform", entity=entity, values=[1.2, 0, 0.15, 0, 0, 0, 1, 1, 1])
    session.command("wait", timeout=5)
    assert job.state == "succeeded"
    assert mesh(session, entity).counts[0] > 100
    assert session.document.entity(entity).matrix[3] == pytest.approx(1.2)


def test_pending_shape_edit_survives_scp_transform(session):
    entity = create(session)
    lift_first_point(session, entity)
    session.command("scp.transform", entity=entity, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.command("wait", timeout=5)
    assert mesh(session, entity).bounds[5] == pytest.approx(0.2)
    assert session.document.entity(entity).matrix[3] == pytest.approx(1)
    assert not session.scheduler.errors


def test_captured_child_anchor_does_not_cycle_pose_following_geometry(session):
    root = session.command("scp.empty", name="Group")
    entity = create(session, root, "BODY")
    hook(session, entity)
    previous = mesh(session, entity)
    session.command("scp.attachment", entity=entity, child_mode="VERTEX_NEAREST")
    session.command("wait", timeout=5)
    assert not session.scheduler.blocked
    assert session.document.entity(entity).status == "ready"
    assert mesh(session, entity) is previous
    assert not session.scheduler.errors


def world_vertices(session, entity):
    frame = entity_frame(session.engine, session.document.entity(entity))
    return components.transformed(session.engine, mesh(session, entity).array(0), frame)


@pytest.mark.parametrize("follow_child", [True, False])
def test_origin_relocation_preserves_deformation_and_following_controls(
    session, assembly, follow_child
):
    root, child = assembly
    control = session.command("control.create", entity=child if follow_child else root)
    hook(session, child, control)
    before = world_vertices(session, child)
    frame = display_frame(session, session.document.control(control))
    session.command("scp.origin", entity=child)
    session.command("wait", timeout=5)
    session.command("evaluate", entities=[child])
    session.command("wait", timeout=5)
    np.testing.assert_allclose(world_vertices(session, child), before, atol=1e-9)
    np.testing.assert_allclose(display_frame(session, session.document.control(control)), frame)
    assert not session.scheduler.errors


def test_ordinary_control_following_survives_save_and_history(session, tmp_path):
    support = create(session)
    control = session.command("control.create", entity=support)
    frame = display_frame(session, session.document.control(control))
    path = str(tmp_path / "attached.anthroforge")
    session.command("save", path=path, blocked_policy="wait")
    session.command("open", path=path)
    lift_first_point(session, support)
    session.command("wait", timeout=5)
    np.testing.assert_allclose(display_frame(session, session.document.control(control)), frame)
    session.command("undo")
    session.command("redo")
    session.command("wait", timeout=5)
    np.testing.assert_allclose(display_frame(session, session.document.control(control)), frame)
    assert session.document.control(control).result.status == "ready"


def test_on_release_shared_hook_is_one_reversible_edit(session):
    entity = create(session)
    control = hook(session, entity)
    session.command("update_mode", entity=entity, mode="ON_RELEASE")
    source = mesh(session, entity)
    drag_hook(session, control)
    session.command("wait", timeout=5)
    assert mesh(session, entity) is source
    session.command("commit")
    session.command("wait", timeout=5)
    assert mesh(session, entity).bounds[5] == pytest.approx(0.4)
    session.command("undo")
    assert mesh(session, entity) is source
    verify_redone_height(session, entity, 0.4)


def verify_redone_height(session, entity, height):
    session.command("redo")
    session.command("wait", timeout=5)
    assert mesh(session, entity).bounds[5] == pytest.approx(height)


def drag_hook(session, control):
    session.command("begin")
    move_control(session, control, 0.2)
    move_control(session, control, 0.4)


def blocked_construction(session, monkeypatch):
    original, gate, started = construction_tasks.compute, Event(), Event()
    session.scheduler.task_schedulers["construction"] = MeasuredTaskScheduler()

    def delayed(*args):
        started.set()
        assert gate.wait(3)
        return original(*args)

    monkeypatch.setattr(construction_tasks, "compute", delayed)
    return gate, started


def wait_for_construction(session, started):
    deadline = monotonic() + 2
    while not started.is_set() and monotonic() < deadline:
        session.scheduler.tick()
        started.wait(0.005)
    assert started.is_set(), "Construction did not dispatch after its curve prerequisite."


def test_running_construction_checkpoint_and_undo_redo(session, tmp_path, monkeypatch):
    entity = create(session)
    before = session.document
    gate, started = blocked_construction(session, monkeypatch)
    lift_first_point(session, entity)
    wait_for_construction(session, started)
    verify_construction_checkpoint(session, entity, before, tmp_path)
    session.command("undo")
    session.command("redo")
    gate.set()
    session.command("wait", timeout=5)
    assert mesh(session, entity).bounds[5] == pytest.approx(0.2)
    assert any(j.state == "obsolete" for j in session.scheduler.jobs)


def verify_construction_checkpoint(session, entity, before, tmp_path):
    job = next(j for j in session.scheduler.jobs if j.active and j.kind == "construction")
    assert job.snapshot is not None
    path = tmp_path / "checkpoint.anthroforge"
    session.command("save", path=str(path), blocked_policy="checkpoint")
    saved, _ = storage.read_package(path, session.engine)
    assert saved.entity(entity).result.asset == before.entity(entity).result.asset
    assert saved.entity(entity).primitive == job.snapshot.entity(entity).primitive


def world_endpoint(session, entity):
    item = session.document.entity(entity)
    # A box's first cross-section has four symmetric vertices around its curve endpoint.
    vertices = mesh(session, entity).array(0)[:4]
    return components.transformed(session.engine, vertices, item.matrix).mean(axis=0)


def bind_endpoint(session, entity, control):
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    return session.command(
        "deformer.add",
        control=control,
        indices=[0, 1, 2],
        target=dict(owner=entity, stage="CURVE", component=curve.id),
    )


def connected_bodies(session):
    root = session.command("scp.empty", name="Assembly")
    first = session.command("primitive.create", kind="BODY", shape="BOX", parent=root)
    second = session.command("primitive.create", kind="BODY", shape="BOX", parent=root)
    session.command("wait", timeout=5)
    control = session.command("control.create", entity=root)
    bindings = [bind_endpoint(session, entity, control) for entity in (first, second)]
    session.command("wait", timeout=5)
    return first, second, control, bindings


def test_cross_scp_endpoints_stay_connected_and_removal_is_local(session):
    first, second, control, bindings = connected_bodies(session)
    session.command("scp.transform", entity=second, values=[0, 0.2, 0.3, 0, 0, 0, 1, 1, 1])
    session.command("wait", timeout=5)
    np.testing.assert_allclose(world_endpoint(session, first), world_endpoint(session, second))
    before = display_frame(session, session.document.control(control))
    session.command("control.follow", control=control, entity=second)
    session.command("wait", timeout=5)
    np.testing.assert_allclose(display_frame(session, session.document.control(control)), before)
    session.command("deformer.remove", binding=bindings[0])
    move_control(session, control, 0.5)
    session.command("wait", timeout=5)
    assert not session.document.entity(first).deformers
    assert session.document.entity(second).deformers[0].id == bindings[1]
    assert not session.scheduler.errors


def write_legacy(path, session):
    manifest = storage.manifest(session.document, session.resources)
    manifest["version"] = 1
    manifest["document"].pop("controls")
    for entity in manifest["document"]["entities"]:
        for key in ("primitive", "deformers", "thickness", "result", "pose_revision"):
            entity.pop(key)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest))
        for key, asset in session.assets.items():
            for kind, label in enumerate(storage.resource_storage.MESH_BUFFERS[:3]):
                storage.resource_storage.write_array(
                    archive, f"assets/{key}/{label}.npy", asset.mesh.array(kind)
                )


def test_legacy_import_is_rejected_without_replacing_current_document(session, tmp_path):
    session.command("import", path="examples/primitives/cube.obj", units=1)
    session.command("wait", timeout=5)
    path = tmp_path / "legacy.anthroforge"
    write_legacy(path, session)
    before = session.document
    with pytest.raises(ValueError, match="Unsupported AnthroForge project"):
        session.command("open", path=str(path))
    assert session.document is before
