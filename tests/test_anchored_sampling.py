"""Native resampling honors required knots, closure, count budgets and cancellation."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import PolylineSettings
from anthroforge.native import paths
from anthroforge.native.mesh import NativeCancellation


def path(session, closed):
    points = ((0, 0, 0), (0.1, 0, 0), (0.1, 2, 0), (1, 2, 0), (1, 0, 0))
    definition = Curve(
        tuple(CurvePoint(position=p) for p in points),
        closed=closed,
        engine_settings=PolylineSettings(),
    )
    return paths.evaluate(session.engine, definition), definition


@pytest.mark.parametrize("closed", [False, True])
def test_anchored_sampling_keeps_short_span_corners_and_exact_count(session, closed):
    source, definition = path(session, closed)
    output, indices = paths.sample_anchored(source, 19, [0, 1, 4])
    assert len(output) == 19 and indices[0] == 0
    np.testing.assert_array_equal(
        output[indices, :3], [definition.points[i].position for i in (0, 1, 4)]
    )
    assert indices[1] == 1
    assert closed or indices[-1] == 18
    assert not closed or np.any(output[-1, :3] != output[0, :3])


def test_invalid_anchor_requests_and_cancellation_fail_explicitly(session):
    source, _ = path(session, False)
    for knots, count in (([0, 1, 2, 3, 4], 3), ([0, 2], 10), ([0, 4, 1], 10), ([1, 4], 10)):
        with pytest.raises(ValueError):
            paths.sample_anchored(source, count, knots)
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        paths.sample_anchored(source, 19, [0, 1, 4], cancel.handle)
