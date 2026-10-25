"""Owner backsolve follows captured material rather than recycled Boolean face ids."""

from dataclasses import replace

import numpy as np

from anthroforge.core.entities import IDENTITY, SCP, Attachment
from anthroforge.core.shortcut_edits import OwnerAnchor
from anthroforge.native import material_bindings, shortcut_attachments
from anthroforge.native.topology import finalize
from tests.test_segment_chain import REFERENCE, construct, source_settings


def thickened(settings):
    first = settings.segments[0]
    return replace(
        settings, segments=(replace(first, radius=first.radius * 1.05), *settings.segments[1:])
    )


def fixture(engine):
    settings = replace(
        source_settings(next(c for c in REFERENCE["cases"] if c["name"] == "Index")), unite=True
    )
    before = construct(engine, settings, 0)
    after = construct(engine, thickened(settings), 0)
    from anthroforge.native.triangle_material import arrays

    a, b = arrays(before)[0][1:], arrays(after)[0][1:]
    count = min(len(a), len(b))
    index = int(np.flatnonzero(a[:count] != b[:count])[0])
    row = (0.0,) * 27 + (float(index),)
    owner = SCP("Owner", asset="before", attachment=Attachment(binding=row))
    return owner, SCP("Parent"), {"before": finalize(before, None, 0), "after": after}


def test_remeshed_owner_preserves_material_anchor(session):
    owner, parent, meshes = fixture(session.engine)
    retained = shortcut_attachments.capture(session.engine, owner, parent, meshes)
    record = shortcut_attachments.material_capture(session.engine, owner, meshes)
    changed = replace(owner, asset="after")
    anchor = OwnerAnchor(*retained, "before", record)
    result = shortcut_attachments.material_backsolve(
        session.engine, changed, parent, meshes, anchor
    )
    resolved = material_bindings.frames(meshes["before"], meshes["after"], result, [record])
    np.testing.assert_allclose(resolved.reshape(4, 4)[:3, 3], retained[3], atol=1e-7)
    indexed = shortcut_attachments.backsolve(session.engine, changed, parent, meshes, retained)
    assert not np.allclose(result, indexed, atol=1e-6)


def test_material_capture_preserves_original_polygon_center(session):
    owner, parent, meshes = fixture(session.engine)
    retained = shortcut_attachments.capture(session.engine, owner, parent, meshes)
    record = shortcut_attachments.material_capture(session.engine, owner, meshes)
    frame = material_bindings.frames(meshes["before"], meshes["before"], IDENTITY, [record])
    np.testing.assert_allclose(frame.reshape(4, 4)[:3, 3], retained[3], atol=1e-7)


def test_source_child_anchor_transfer_preserves_baseline_pose(session, assembly):
    from threading import Event

    from anthroforge.native.attachments import propagate

    root, child = assembly
    before, parent = session.document.entity(child), session.document.entity(root)
    origin = tuple(v + 0.01 for v in before.attachment.binding[18:21])
    row = shortcut_attachments.retain_child_anchor(session.engine, before, origin)
    changed = replace(before, attachment=replace(before.attachment, binding=row))
    meshes = {key: asset.mesh for key, asset in session.assets.items()}
    result = propagate(session.engine, [parent, changed], meshes, {child}, Event())[-1]
    np.testing.assert_allclose(result.matrix, before.matrix, atol=1e-7)
    assert row[27] == -1 and row[18:21] == origin
