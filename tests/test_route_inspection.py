"""Native route evidence uses production input resolution without publishing anatomy."""

import numpy as np
import pytest

from anthroforge.native import routing, routing_trace
from anthroforge.native.mesh import NativeCancellation
from tests.conftest import CUBE
from tests.test_fiber_creation import bind, scene
from tests.test_native_routing import curve
from tests.test_routing_workflow import accepted, convert, create


def inspect(session, key, **options):
    session.command("curve.inspect.route", target=key, **options)
    session.wait(20)
    result = session.command("curve.inspect.status")
    assert result["state"] == "ready", result
    return result["report"]


@pytest.mark.parametrize("backend", ["CUSTOM", "PIQP"])
def test_native_trace_preserves_production_result(session, backend):
    inputs = routing.Inputs(curve([(0, 0, 0), (1, 1, 0), (3, 0, 0)]), backend=backend)
    path, report = routing.evaluate(session.engine, inputs)
    trace = routing_trace.inspect(session.engine, inputs)
    assert trace["success"] and trace["counters"] == list(report.counters)
    assert {r["stage"] for r in trace["records"]} == set(routing_trace.STAGES)
    assert all(not r["termination"] for r in trace["records"] if r["stage"] != "Solver trial")
    ends = [r["points"] for r in trace["records"] if r["stage"] == "Final"]
    points = np.asarray(ends[0][:-1] + ends[1])
    np.testing.assert_array_equal(points, path.array()[:, :3])


def test_trace_is_read_only_and_stale_after_authoring(session):
    key = create(session)
    before, history = session.document, len(session.history.entries)
    report = inspect(session, key)
    assert session.document is before and len(session.history.entries) == history
    assert report["warm"] and report["accepted_asset"] == before.object(key).result.asset
    session.command(
        "curve.point.update", curve=key, point=before.object(key).points[0].id, position=[-2, 0, 0]
    )
    assert session.command("curve.inspect.status")["state"] == "stale"


def test_fiber_trace_uses_resolved_bindings_and_cold_planner(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    convert(session, fiber.id)
    session.command("scp.transform", entity=target, values=[0, 0, 1, 0, 0, 0, 1, 1, 1])
    session.wait(20)
    report = inspect(session, fiber.id, cold=True)
    assert report["success"] and not report["warm"]
    assert report["owners"][0] == 1 and report["surfaces"][0]["target"] == target
    records = [r for r in report["records"] if r["stage"] == "Final"]
    result = accepted(session, fiber.id).path.array()
    np.testing.assert_allclose(records[0]["points"][0], result[0, :3], atol=1e-10)
    np.testing.assert_allclose(records[-1]["points"][-1], result[-1, :3], atol=1e-10)


def test_native_trace_cancellation_is_not_reported_as_solver_failure(session):
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        routing_trace.inspect(
            session.engine, routing.Inputs(curve([(0, 0, 0), (1, 0, 0)])), cancel.handle
        )


def test_failed_planner_keeps_reference_evidence_and_accepted_result(session):
    bone = session.command("import", path=str(CUBE), units=1)["entity_id"]
    session.wait()
    key = create(session, (bone,))
    old = session.document.object(key)
    session.command("curve.point.update", curve=key, point=old.points[0].id, position=[0, 0, 0])
    session.wait()
    report = inspect(session, key, cold=True)
    assert not report["success"] and "intersects" in report["error"]
    assert report["records"][0]["stage"] == "Reference"
    assert session.document.object(key).result.asset == old.result.asset


def test_bounded_capture_reports_omitted_records_without_changing_solve(session):
    inputs = routing.Inputs(curve([(i, i % 2, 0) for i in range(140)]))
    report = routing_trace.inspect(session.engine, inputs)
    assert report["success"] and report["omitted"] > 0
    assert len(report["records"]) <= report["limits"]["records"]
    assert sum(len(row["points"]) for row in report["records"]) <= report["limits"]["points"]
