"""Independent copies remap resource owners and preserve accepted Manual inputs."""

import numpy as np

from tests.test_fiber_consumers import differential_fiber
from tests.test_fiber_creation import path


def body(session, fiber, parent):
    key = session.command("primitive.from_curves", curves=[fiber], kind="BODY", parent=parent)
    session.wait()
    return key


def duplicated_fiber(session):
    parent, fiber = differential_fiber(session)
    body(session, fiber, parent)
    root = session.command("scp.duplicate", entity=parent)
    session.wait()
    consumer = next(
        e for e in session.document.entities if e.parent == root and e.primitive.kind == "BODY"
    )
    copied = session.document.object(consumer.primitive.curves[0].id)
    return root, fiber, copied


def test_duplicate_remaps_dense_supports_not_only_endpoint_labels(session):
    root, original, copied = duplicated_fiber(session)
    source = session.document.object(original)
    assert not set(copied.supports) & set(source.supports)
    asset = session.resources.attachments[copied.attachment_asset]
    assert set(asset.targets) == set(copied.supports)
    assert root in {b.target for b in copied.bindings}
    before = path(session, copied.id)
    other = source.bindings[-1].target
    session.command("scp.transform", entity=other, values=[1.5, 0, 2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_array_equal(path(session, copied.id), before)
    assert session.document.object(copied.id).result.status == "ready"


def independent_pending(session):
    parent, fiber = differential_fiber(session)
    consumer = body(session, fiber, parent)
    session.command("update_mode", entity=fiber, mode="MANUAL")
    source = session.document.object(fiber)
    session.command("curve.point.remove", curve=fiber, point=source.points[1].id)
    copied = session.command("primitive.make_independent", entity=consumer, curve=fiber)
    session.wait()
    return fiber, copied, consumer


def test_independent_pending_copy_retains_displayed_result_and_baseline(session, tmp_path):
    original, copied, consumer = independent_pending(session)
    item = session.document.object(copied)
    assert item.edit and item.edit.baseline != session.document.object(original).edit.baseline
    assert item.result.asset and session.document.entity(consumer).result.status == "ready"
    np.testing.assert_array_equal(path(session, copied), path(session, original))
    location = tmp_path / "copy.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    session.command("curve.evaluate", curve=copied)
    session.wait()
    assert session.document.object(copied).result.status == "ready"
    assert session.document.object(copied).edit is None and session.document.object(original).edit
