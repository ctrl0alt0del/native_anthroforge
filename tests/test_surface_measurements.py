"""Measurements cover transformed extents, section spans, cancellation and read-only use."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection_metrics
from anthroforge.native.mesh import NativeCancellation
from tests.test_mesh_replacement import source
from tests.test_tissue_interaction import controller as controller


def test_extent_axes_and_section_spans_use_world_coordinates(session):
    target = source(session)
    mesh = session.assets[session.document.entity(target).result.asset].mesh
    frame = np.array(IDENTITY).reshape((4, 4))
    frame[:3, :3] *= [2, 3, 4]
    result = inspection_metrics.measure(mesh, frame.ravel())
    np.testing.assert_allclose(result["extents"], [2, 3, 4])
    cut = inspection_metrics.section(mesh, frame.ravel(), [0, 0, 1, 0])
    assert cut["available"] and not cut["truncated"]
    np.testing.assert_allclose(sorted(cut["spans"]), [2, 3])
    for line, axis in zip(np.array(cut["lines"]).reshape((2, 2, 3)), cut["axes"], strict=True):
        assert np.dot(line[1] - line[0], axis) > 0


def test_empty_section_and_cooperative_cancellation(session):
    target = source(session)
    mesh = session.assets[session.document.entity(target).result.asset].mesh
    assert not inspection_metrics.section(mesh, IDENTITY, [0, 0, 1, 100])["available"]
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        inspection_metrics.measure(mesh, IDENTITY, cancel.handle)
    with pytest.raises(ValueError, match="dimensions"):
        inspection_metrics.measure(mesh, [1])


def test_async_measurement_and_non_tissue_section_preserve_document(controller):
    session = controller.session
    target = source(session)
    controller.refresh()
    controller.select(target)
    before, cursor = session.document, session.history.cursor
    controller.section_tools.enable(True)
    controller.surface_measurements.show(target, "final")
    controller.surface_measurements.submit()
    session.wait()
    controller.surface_measurements.synchronize()
    report = controller.surface_measurements.state["report"]
    assert report["section"]["available"] and report["conditioning"]["boundary_edges"] == 0
    assert session.document is before and session.history.cursor == cursor
