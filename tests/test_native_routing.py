"""Owned production routing kernel contracts, independent of desktop and Blender."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.native import routing
from anthroforge.native.mesh import NativeCancellation


def curve(points, closed=False):
    return Curve(
        tuple(CurvePoint(position=tuple(p)) for p in points),
        closed=closed,
        engine_settings=RoutingSettings(samples=32),
    )


def test_routing_preserves_structural_points_and_sample_correspondence(session):
    source = curve([(0, 0, 0), (1, 1, 0), (3, 0, 0)])
    path, report = routing.evaluate(session.engine, routing.Inputs(source))
    assert path.count == 32 and report.counters[7] == 2
    parameters, samples = path.array(1), path.array()
    for i, point in enumerate(source.points):
        np.testing.assert_allclose(samples[parameters == i, :3], [point.position], atol=1e-12)
    assert np.all(np.isfinite(samples)) and np.all(np.diff(parameters) > 0)


def test_closed_routing_has_no_duplicate_endpoint(session):
    source = curve([(0, 0, 0), (1, 1, 0), (2, 0, 0)], True)
    path, report = routing.evaluate(session.engine, routing.Inputs(source))
    assert path.closed and path.count == 32 and report.counters[7] == 1
    assert not np.allclose(path.array()[0, :3], path.array()[-1, :3])
    assert path.array(1)[-1] < 3


def test_routing_cancellation_and_malformed_membership_are_rejected(session):
    source = curve([(0, 0, 0), (1, 1, 0)])
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        routing.evaluate(session.engine, routing.Inputs(source), cancel.handle)
    with pytest.raises(ValueError, match="one owner per knot"):
        routing.evaluate(session.engine, routing.Inputs(source, owners=(0,)))
