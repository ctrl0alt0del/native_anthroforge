"""Pin assessment is advisory; approved repairs reject stale plans and commit atomically."""

from dataclasses import replace

import numpy as np
import pytest

from anthroforge.application.issues import fiber_pins
from tests.test_fiber_creation import bind, path, scene


def damaged(session):
    fiber = bind(session, *scene(session))
    broken = []
    for binding in fiber.bindings:
        record = (999999.0,) * 3 + binding.attachment.binding[3:]
        broken.append(replace(binding, attachment=replace(binding.attachment, binding=record)))
    item = replace(fiber, bindings=tuple(broken), generation=fiber.generation + 1)
    session.replace_document(
        objects=tuple(item if o.id == fiber.id else o for o in session.document.objects)
    )
    return item


def scan(session, fiber):
    session.command("fiber.pins.check", curves=[fiber.id])
    session.wait()
    report = session.command("issues.list", filters=dict(provider=fiber_pins.NAME))
    assert all(row["code"] == fiber_pins.REPAIR for row in report["records"]), report
    return report["records"]


def test_assessment_keeps_document_and_approval_repairs_both_pins(session):
    fiber = damaged(session)
    before, shape, count = session.document, path(session, fiber.id), len(session.history.entries)
    rows = scan(session, fiber)
    assert len(rows) == 2 and session.document is before
    session.command("fiber.pins.repair", identities=[row["id"] for row in rows])
    session.wait()
    assert not session.scheduler.errors
    assert len(session.history.entries) == count + 1
    current = session.document.object(fiber.id)
    assert all(b.attachment.binding[0] != 999999 for b in current.bindings)
    np.testing.assert_allclose(path(session, fiber.id), shape, atol=1e-10)
    assert not scan(session, current)


def test_stale_approval_rejects_entire_batch(session):
    fiber = damaged(session)
    rows = scan(session, fiber)
    session.command(
        "scp.transform",
        entity=session.document.entities[0].id,
        values=[0.2, 0, 0, 0, 0, 0, 1, 1, 1],
    )
    session.wait()
    before = session.document
    with pytest.raises(ValueError, match="stale"):
        session.command("fiber.pins.repair", identities=[row["id"] for row in rows])
    assert session.document == before


def test_healthy_pins_need_no_repair_and_scan_has_no_undo(session):
    fiber = bind(session, *scene(session))
    count = len(session.history.entries)
    assert not scan(session, fiber)
    assert len(session.history.entries) == count
