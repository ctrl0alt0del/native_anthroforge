"""Role-aware tissue anchors retain bind-time material topology and offset across updates."""

import numpy as np

from anthroforge.application.resources import referenced
from anthroforge.native import point_attachments
from tests.test_material_bindings import IDENTITY, side_triangle
from tests.test_tissue_workflow import assembly, roundtrip


def bound_to_second_side(session):
    _, _, target = assembly(session)
    session.command("tissue.configure", target=target, changes=dict(both_sides=True))
    session.command("tissue.inflation", target=target, side="b", changes=dict(amount=0.08))
    session.wait()
    item = session.document.object(target)
    mesh = session.assets[item.final_result.asset].mesh
    triangle = mesh.array(0)[mesh.array(3)[side_triangle(mesh, 2)]]
    position = triangle.mean(axis=0).tolist()
    point = session.command("construction.point.create", position=position)
    anchor = session.command("anchor.create", source=point, parent=target, role="TISSUE_FINAL")[
        "object_id"
    ]
    session.wait()
    return target, session.document.object(anchor)


def test_compaction_preserves_attachment_side_material_and_saved_reference(session, tmp_path):
    target, anchor = bound_to_second_side(session)
    captured = anchor.binding.material_asset
    session.command("tissue.inflation", target=target, side="a", changes=dict(enabled=False))
    session.wait()
    current = session.document.object(anchor.id)
    assert current.result.status == "ready", current.result.error
    assert current.binding == anchor.binding
    np.testing.assert_allclose(current.resolved_position, anchor.resolved_position, atol=1e-10)
    assert captured in referenced(session.document)["meshes"]
    roundtrip(session, tmp_path / "material-anchor.anthroforge")
    assert session.document.object(anchor.id).binding == anchor.binding
    session.command("tissue.inflation", target=target, side="b", changes=dict(amount=0.16))
    session.wait()
    assert session.document.object(anchor.id).result.status == "ready"


def test_merged_zero_sides_resolve_and_restore_without_recapture(session):
    target, anchor = bound_to_second_side(session)
    for side in ("a", "b"):
        session.command("tissue.inflation", target=target, side=side, changes=dict(enabled=False))
    session.wait()
    assert session.document.object(anchor.id).result.status == "ready"
    for side in ("a", "b"):
        session.command("tissue.inflation", target=target, side=side, changes=dict(enabled=True))
    session.wait()
    current = session.document.object(anchor.id)
    assert current.result.status == "ready", current.result.error
    assert current.binding == anchor.binding
    np.testing.assert_allclose(current.resolved_frame, anchor.resolved_frame, atol=1e-10)


def test_radial_material_keeps_angular_identity_instead_of_source_point_only(session):
    from tests.test_anchor_operations import scene

    _, _, source = scene(session)
    target = session.command("tissue.create", source=source.id, preset="CUSTOM")
    session.wait()
    point = session.command("construction.point.create", position=[0.03, 0, 0.7])
    key = session.command("anchor.create", source=point, parent=target)["object_id"]
    session.wait()
    binding = session.document.object(key).binding
    session.command("tissue.inflation", target=target, changes=dict(amount=0.08))
    session.wait()
    verify_canonical(session, target, key, binding)


def verify_canonical(session, target, key, binding):
    item = session.document.object(key)
    assert item.result.status == "ready", item.result.error
    current = session.document.object(target).final_result.asset
    handle = session.assets[current].mesh.handle
    expected = point_attachments.resolve(
        session.engine, [handle], [IDENTITY], [0], [binding.attachment.binding]
    )[0]
    np.testing.assert_allclose(item.resolved_frame, expected, atol=1e-10)
