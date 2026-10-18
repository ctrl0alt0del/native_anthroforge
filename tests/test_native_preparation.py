"""Native preparation preserves deformation, connectivity and mixed-frame editing."""

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.core.construction import Control, Deformer, Target
from anthroforge.core.document import Document
from anthroforge.core.entities import IDENTITY
from anthroforge.desktop import authoring_actions, authoring_state
from anthroforge.native import components, construction, control_geometry
from anthroforge.native.mesh import NativeCancellation

WEIGHTS = [
    ({}, [1, 1, 1]),
    ({"invert": True}, [1, 1, 1]),
    ({"restrict": True}, [0, 0, 0]),
    ({"indices": (0, 2, 2147483647)}, [1, 0, 1]),
    ({"weights": (0.1, 0.4, 1.0)}, [0.1, 0.4, 1]),
    ({"weights": (0.1, 0.4, 1.0), "invert": True}, [0.9, 0.6, 0]),
    ({"weights": (0.1, 0.4, 1.0), "invert": True, "indices": (0, 2)}, [0.9, 0, 0]),
]


@pytest.mark.parametrize("settings,expected", WEIGHTS)
@pytest.mark.parametrize("kind", ["HOOK", "LATTICE"])
def test_influence_semantics_through_deformation(session, kind, settings, expected):
    engine, points = session.engine, np.zeros((3, 3))
    binding = Deformer(kind, "control", Target("owner"), **settings)
    if kind == "HOOK":
        target = engine.transform([1, 0, 0, 0, 0, 0, 1, 1, 1])
        result = construction.hook(engine, points, binding, IDENTITY, target, 0)
    else:
        cage_points = construction.lattice_grid(engine, (2, 2, 2)) + [1, 0, 0]
        cage = Control("Cage", "LATTICE", points=tuple(map(tuple, cage_points)))
        result = construction.lattice(engine, points, cage, binding, IDENTITY, IDENTITY, 0)
    assert result[:, 0] == pytest.approx(expected)
    np.testing.assert_array_equal(result[:, 1:], 0)
    np.testing.assert_array_equal(points, 0)


def test_influence_length_and_cancellation(session):
    engine = session.engine
    binding = Deformer("HOOK", "control", Target("owner"), weights=(0.5,))
    with pytest.raises(ValueError, match="Influence weights"):
        construction.hook(engine, [[0, 0, 0]] * 2, binding, IDENTITY, IDENTITY, 0)
    cancel = NativeCancellation(engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        construction.hook(
            engine, [[0, 0, 0]], replace(binding, invert=True), IDENTITY, IDENTITY, cancel.handle
        )


@pytest.mark.parametrize(
    "closed,group,indices",
    [
        (False, 3, [0, 1, 1, 2, 3, 4, 4, 5]),
        (True, 3, [0, 1, 1, 2, 2, 0, 3, 4, 4, 5, 5, 3]),
        (False, 0, [0, 1, 1, 2, 2, 3, 3, 4, 4, 5]),
    ],
)
def test_polyline_order_and_frames(session, closed, group, indices):
    engine = session.engine
    points = np.arange(18, dtype=float).reshape((-1, 3))
    frame = engine.transform([1, 2, 3, 15, 25, 35, -2, 3, 1])
    lines = control_geometry.polylines(engine, points, frame, closed, group)
    expected = components.transformed(engine, points[indices], frame)
    np.testing.assert_allclose(lines, expected, atol=1e-12)
    assert control_geometry.polylines(engine, [], frame).shape == (0, 3)


@pytest.mark.parametrize("resolution", [(1, 1, 1), (1, 3, 2), (2, 2, 2), (10, 10, 10)])
def test_cage_edges_preserve_grid_connectivity(session, resolution):
    engine = session.engine
    points = construction.lattice_grid(engine, resolution)
    frame = engine.transform([1, 2, 3, 15, 25, 35, -2, 3, 1])
    u, v, w = resolution
    indices = reference_grid_edges(resolution)
    expected = components.transformed(engine, points[indices], frame)
    result = control_geometry.cage_lines(engine, points, resolution, frame)
    np.testing.assert_allclose(result, expected, atol=1e-12)
    assert len(result) == 2 * ((u - 1) * v * w + u * (v - 1) * w + u * v * (w - 1))


def reference_grid_edges(resolution):
    u, v, w = resolution
    return [
        k
        for i in range(u * v * w)
        for s, n in zip((1, u, u * v), resolution, strict=True)
        if i // s % n + 1 < n
        for k in (i, i + s)
    ]


def test_display_buffer_validation(session):
    with pytest.raises(ValueError, match="polyline"):
        control_geometry.polylines(session.engine, [[0, 0, 0]] * 3, IDENTITY, group=2)
    with pytest.raises(ValueError, match="resolution"):
        control_geometry.cage_lines(session.engine, [[0, 0, 0]], (2, 2, 2), IDENTITY)


def mixed_cage_editor(session):
    grid = tuple(map(tuple, construction.lattice_grid(session.engine, (2, 2, 2))))
    a = Control("A", "LATTICE", points=grid)
    matrix = session.engine.transform([1, 2, 3, 15, 25, 35, -2, 3, 1])
    b = replace(a, id="B", matrix=matrix)
    session.document = Document(controls=(a, b), update_mode="MANUAL")
    rows_a, rows_b = (authoring_state.control_components(session, c) for c in (a, b))
    rows = [row for pair in zip(rows_a, rows_b, strict=True) for row in pair]
    return SimpleNamespace(controller=SimpleNamespace(session=session), drag_rows=rows), (a, b)


def test_grouped_edit_preserves_interleaved_frames_and_cancel(session):
    editor, controls = mixed_cage_editor(session)
    before = session.document
    world = np.array([row[1] for row in editor.drag_rows]) + [0.2, -0.3, 0.1]
    session.command("begin")
    authoring_actions.apply_points(editor, world)
    actual = [
        authoring_state.control_components(session, session.document.control(c.id))
        for c in controls
    ]
    for index, rows in enumerate(actual):
        np.testing.assert_allclose([r[1] for r in rows], world[index::2], atol=1e-12)
    session.command("cancel")
    assert session.document.controls == before.controls


def test_grouped_transform_rejects_missing_coordinates_before_edit(session):
    editor, _ = mixed_cage_editor(session)
    before = session.document
    with pytest.raises(ValueError, match="selected components"):
        authoring_actions.apply_points(editor, [])
    assert session.document is before
