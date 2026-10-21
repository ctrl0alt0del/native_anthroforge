"""All completed drawing/point gestures use the shared exterior query boundary."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import strokes, surface_queries
from tests.test_fiber_creation import scene
from tests.test_strokes import pointer, stroke
from tests.test_surface_query_modes import compound


def projection(target):
    return dict(targets=[target], queries=[[x, 0, 2, 0, 0, -1, 0.02, 1] for x in (-0.2, 0.2)])


@pytest.mark.parametrize("operation", ["curve.create", "curve.draw"])
def test_created_points_finalize_in_one_undo(session, operation):
    target, _ = scene(session)
    before = session.history.cursor
    args = dict(points=[[-0.2, 0, 0.25], [0.2, 0, 0.25]], projection=projection(target))
    if operation == "curve.create":
        args["points"] = [dict(position=p) for p in args["points"]]
    result = session.command(operation, **args)
    key = result if isinstance(result, str) else result["object_id"]
    session.wait()
    np.testing.assert_allclose(
        [p.position[2] for p in session.document.object(key).points], 0.52, atol=1e-6
    )
    assert session.history.cursor == before + 1
    session.navigate(-1)
    assert key not in session.document.registry.records


def test_final_stroke_queries_exclude_cavity_and_leave_unsnapped_samples(session):
    source = compound(session.engine)
    value = stroke(session, [source.handle], [IDENTITY])
    value.snapping(True)
    value.append([0, 0, 0, 0, 0, 1, 0, 0, 1], False)
    value.snapping(False)
    value.append(pointer(0.2), False)
    raw, intent = value.read(), value.placements()
    assert raw[0, 2] < 0.3 and list(intent[:, 7]) == [1, 0]
    query = surface_queries.prepare(source, None, surface_queries.Mode.CONFIRMED)
    final = strokes.confirmed(session.engine, [query.mesh.handle], [IDENTITY], raw, intent)
    assert 0.5 < final[0, 2] < 0.500001
    np.testing.assert_array_equal(final[1], raw[1])
    value.pop()
    assert value.placements().shape == (1, 8)


def test_cursor_is_confirmed_without_anatomical_undo(session):
    target, _ = scene(session)
    before = session.history.cursor
    job = session.command(
        "cursor.place.surface", targets=[target], origin=[0, 0, 2], direction=[0, 0, -1]
    )
    session.wait()
    assert session.scheduler.registry.by_id[job].state == "succeeded"
    assert 0.5 < session.workspace.cursor[2] < 0.500001
    assert session.history.cursor == before


def test_later_numeric_cursor_edit_supersedes_pending_query(session):
    target, _ = scene(session)
    session.command(
        "cursor.place.surface", targets=[target], origin=[0, 0, 2], direction=[0, 0, -1]
    )
    session.command("workspace.update", cursor=[4, 5, 6])
    session.wait()
    assert session.workspace.cursor == (4, 5, 6)
