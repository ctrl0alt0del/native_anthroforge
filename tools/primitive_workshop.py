"""Inspect the complete runnable API example in the production desktop."""

import json
from pathlib import Path

from primitive_acceptance import OUTPUT, screenshot, settle
from PySide6.QtTest import QTest

from anthroforge.authoring import dispatch


def populate(controller):
    requests = json.loads(Path("examples/primitives.json").read_text())
    requests[-2]["arguments"]["path"] = str(OUTPUT / "workshop.anthroforge")
    results = {}
    for request in requests:
        dispatch(controller.session, request, results)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    controller.refresh()
    settle(controller)


def capture_entity(controller, window, name, filename):
    entity = next(e for e in controller.session.document.entities if e.name == name)
    assert entity.result.status == "ready"
    assert not entity.primitive or entity.result.asset
    controller.selection_view.select(entity.id)
    controller.authoring.setEditing(True)
    controller.viewport_view.frameSelection()
    settle(controller)
    QTest.qWait(150)
    screenshot(window, filename)


def verify(controller, window):
    window.resize(1600, 1000)
    populate(controller)
    capture_entity(controller, window, "Primitive workshop", "workshop-group")
    capture_entity(controller, window, "Connected loft", "workshop-loft")
    capture_entity(controller, window, "Curved capsule", "workshop-body")
    return dict(
        headless_example=True,
        group_framing=True,
        loft_geometry=True,
        curved_body=True,
        persistence=True,
    )
