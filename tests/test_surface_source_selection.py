"""Source discovery and ordered batch selection never edit construction geometry."""

import pytest

from tests.test_surface_workflow import curve, surface
from tests.test_tissue_interaction import controller as controller


def test_source_query_and_selection_preserve_order_and_document(controller):
    session = controller.session
    sources = [curve(session, y) for y in (0, 0.2, 0.4)]
    target = surface(session, sources)
    controller.refresh()
    controller.selection_view.select(target)
    before, count = session.document, len(session.history.entries)
    assert session.command("surface.source_ids", target=target) == sources
    controller.selection_view.selectSurfaceSources(target)
    assert (
        controller.selection_view.selectedObjects == sources and controller.selection == sources[-1]
    )
    assert session.document is before and len(session.history.entries) == count
    controller.selection_view.selectObjects([sources[0], sources[0], sources[1]])
    assert controller.selection_view.selectedObjects == sources[:2]


def test_invalid_batch_selection_keeps_existing_selection(controller):
    key = curve(controller.session)
    controller.refresh()
    controller.selection_view.select(key)
    with pytest.raises(ValueError, match="absent"):
        controller.selection_view.selectObjects([key, "missing"])
    assert controller.selection_view.selectedObjects == [key]
