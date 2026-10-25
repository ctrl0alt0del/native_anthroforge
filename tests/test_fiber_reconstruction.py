"""Independent dense objective checks the native sparse and prefix-filter paths."""

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import BezierSettings
from anthroforge.core.entities import IDENTITY
from anthroforge.native import attachment_fields as fields
from anthroforge.native import construction, fiber_deformation, paths
from tests.test_fiber_creation import CUBE


def curve_definition(resolution, closed):
    points = [(0, 0, 0.7), (0.75, 0.2, 0.8), (1.5, 0, 0.7)]
    return Curve(
        tuple(CurvePoint(position=p) for p in points),
        engine_settings=BezierSettings(resolution),
        closed=closed,
    )


def capture(session, resolution, closed):
    engine, curve = session.engine, curve_definition(resolution, closed)
    mesh = engine.import_mesh(CUBE, 1, False)
    path = paths.evaluate(engine, curve)
    frames = [IDENTITY, engine.transform([1.5, 0, 0, 0, 0, 0, 1, 1, 1])]
    spec = fields.Capture(
        path, construction.resolved_curve(engine, curve), IDENTITY, [0, 2], [0, 1]
    )
    field = fields.capture(engine, ([mesh.handle] * 2, frames), spec)
    moved = [frames[0], engine.transform([1.5, 0, 1, 0, 0, 0, 1, 1, 1])]
    return mesh, field, moved


def stations(field):
    points = field.path.array()[:, :3]
    arc = np.r_[0, np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))]
    length = arc[-1] + (np.linalg.norm(points[0] - points[-1]) if field.path.closed else 0)
    steps = np.diff(np.r_[arc, length])
    previous = np.r_[steps[-1] if field.path.closed else 0, steps[:-1]]
    mass = (previous + steps) / (2 * length)
    if not field.path.closed:
        mass[-1] = previous[-1] / (2 * length)
    return arc / length, mass


def kernel(value):
    value = np.minimum(np.abs(value), 1)
    return (1 - value) ** 4 * (1 + 4 * value)


def distances(a, b, closed):
    result = np.abs(a - b)
    return np.minimum(result, 1 - result) if closed else result


def weights(field, arc, mass, pins):
    original = np.where(field.owners == 1, field.weights, 0).sum(axis=1)[: len(arc)]
    matrix = kernel(distances(arc[:, None], arc, field.path.closed) / 0.2) * mass
    result = (matrix @ original) / matrix.sum(axis=1)
    width = min(0.2, 0.45 * distances(arc[pins[0]], arc[pins[1]], field.path.closed))
    for pin, goal in zip(pins, (0, 1), strict=True):
        influence = kernel(distances(arc, arc[pin], field.path.closed) / width)
        result = result * (1 - influence) + goal * influence
    return result


def laplacian(arc, closed):
    count = len(arc)
    result = np.zeros((count, count))
    for i in range(0 if closed else 1, count if closed else count - 1):
        before, after = (i - 1) % count, (i + 1) % count
        a = arc[i] - arc[before] if i else 1 - arc[before]
        b = arc[after] - arc[i] if after else 1 - arc[i]
        result[i, [before, i, after]] = [2 / (a * (a + b)), -2 / (a * b), 2 / (b * (a + b))]
    return result


def reference(field, goals):
    points = field.path.array()[:, :3]
    arc, mass = stations(field)
    pins = np.searchsorted(field.path.array(1), [0, 2])
    raw = points + weights(field, arc, mass, pins)[:, None] * [0, 0, 1]
    difference = laplacian(arc, field.path.closed)
    bending = 0.2**4 * difference.T * mass
    hessian = np.diag(mass) + bending @ difference
    free = np.setdiff1d(np.arange(len(points)), pins)
    rhs = mass[:, None] * raw + bending @ difference @ points
    rhs = rhs[free] - hessian[np.ix_(free, pins)] @ goals
    output = raw.copy()
    output[free], output[pins] = np.linalg.solve(hessian[np.ix_(free, free)], rhs), goals
    return output


@pytest.mark.parametrize("resolution", [24, 270])
@pytest.mark.parametrize("closed", [False, True])
def test_regional_translation_matches_dense_objective(session, resolution, closed):
    mesh, field, frames = capture(session, resolution, closed)
    goals = fields.resolved_points(session.engine, ([mesh.handle] * 2, frames), field, 0)
    goals = goals[[field.path.count, field.path.count + 6]]
    prepared = fiber_deformation.prepare(session.engine, field, [mesh] * 2, [0, 2], [0, 1], 0)
    actual = fiber_deformation.evaluate(prepared, [mesh.handle] * 2, frames, goals, 0)
    expected = reference(field, goals)
    np.testing.assert_allclose(actual[: field.path.count], expected, atol=2e-7)
    np.testing.assert_array_equal(actual[[0, np.searchsorted(field.path.array(1), 2)]], goals)
