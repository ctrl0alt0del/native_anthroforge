"""Relationship findings never reshape the strict reflected source geometry."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application import surface_providers
from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.surface_references import SurfaceReference


def shared_anchor(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True)
    point = session.command("construction.point.create", position=[1, 0, 0])
    anchor = session.command("anchor.create", source=point, parent=child)["object_id"]
    session.command("wait")
    session.command("mirror.attachment.share", source=anchor, binding="binding")
    session.command("wait")
    return root, child, anchor


def test_asymmetric_shared_target_reports_mismatch_without_moving_anchor(session, assembly):
    root, child, anchor = shared_anchor(session, assembly)
    before = session.document.object(anchor)
    rows = session.command("mirror.attachment.inspect", target=MirrorInstance(anchor, root).id)
    assert rows[0]["status"] == "mismatch", rows
    assert rows[0]["residual"] > 0.9
    assert session.document.object(anchor) is before
    assert any(
        v.code == "MIRROR_ATTACHMENT_MISMATCH" for v in session.issues.repository.records.values()
    )


def test_source_removal_is_blocked_before_any_consumer_binding_is_rewritten(session, assembly):
    root, child, anchor = shared_anchor(session, assembly)
    point = session.command("construction.point.create", position=[-1, 0, 0])
    dependent = session.command(
        "anchor.create", source=point, parent=MirrorInstance(child, root).id
    )
    session.command("wait")
    before = session.document
    with pytest.raises(ValueError, match="referenced consumers"):
        session.command("scp.delete", entity=root)
    assert session.document == before
    assert session.document.object(dependent["object_id"]).binding.reference.instance == root


def test_mirrored_provider_and_binding_are_unchanged_by_source_failure(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True)
    ref = SurfaceReference(child, instance=root)
    original = surface_providers.get(session.engine, session.document, session.assets, ref)
    failed = replace(session.document.entity(child), status="failed", error="Fixture failure")
    session.replace_document(
        entities=tuple(failed if e.id == child else e for e in session.document.entities)
    )
    retained = surface_providers.get(session.engine, session.document, session.assets, ref)
    assert retained.resource is original.resource
    np.testing.assert_array_equal(retained.frame, original.frame)
