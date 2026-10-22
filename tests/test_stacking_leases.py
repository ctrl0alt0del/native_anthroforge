"""Multi-call stacking ownership, invalidation and metadata-only native planning."""

import numpy as np
import pytest

from anthroforge.native import components, stacking_abi
from anthroforge.native.mesh import INT64, pointer
from anthroforge.native.stacking import StackSession
from anthroforge.native.stacking_leases import acquire
from tests.stacking_fixtures import domain, settings
from tests.test_tissue_stack_workflow import assembly as tissue_assembly
from tests.test_tissue_stacking_native import CASES, assert_same_output


def test_checked_out_session_is_exclusive_and_successful_session_is_reused(session):
    with acquire(session.engine, "receiver") as first:
        with acquire(session.engine, "receiver") as other:
            assert first.handle != other.handle
        with acquire(session.engine, "receiver") as reused:
            assert reused is other


def test_failed_session_is_discarded_and_not_available_to_next_job(session):
    with pytest.raises(ValueError, match="failed"):
        with acquire(session.engine, "receiver") as failed:
            raise ValueError("failed")
    assert not session.engine.stack_sessions.retained()
    with acquire(session.engine, "receiver") as next_job:
        assert next_job is not failed


def test_clearing_cache_during_execution_does_not_resurrect_retained_context(session):
    with acquire(session.engine, "receiver"):
        session.engine.clear_caches()
    assert not session.engine.stack_sessions.retained()


def test_metadata_plan_preserves_diagnostics_without_copying_output_points(session, monkeypatch):
    case = CASES[0]
    packed = [domain(row) for row in case["domains"]]
    native = StackSession(session.engine)
    full, order = native.plan([r[0] for r in packed], settings(case["settings"]))
    monkeypatch.setattr(native.engine.library, "af_stack_points", lambda *a: pytest.fail("copied"))
    metadata, next_order = native.plan(
        [r[0] for r in packed], settings(case["settings"]), metadata_only=True
    )
    assert len(next_order) == len(order)
    assert metadata == {
        key: {name: row[name] for name in ("status", "message")} for key, row in full.items()
    }
    assert native.bytes > 0


def obstacle_variants(session, assembly):
    mesh = session.assets[session.document.entity(assembly[0]).asset].mesh
    frame = session.engine.transform([1, 2, 3, 15, 20, 30, 0.7, 2, 1])
    vertices = components.transformed(session.engine, mesh.array(0), frame)
    faces = np.asarray(mesh.array(3), dtype=np.int64)
    legacy = stacking_abi.Obstacle(
        pointer(vertices), faces.ctypes.data_as(INT64), len(vertices), len(faces)
    )
    native = stacking_abi.Obstacle(mesh=mesh.handle)
    native.frame[:] = frame
    return (legacy, native), (mesh, vertices, faces)


def test_handle_obstacles_preserve_transformed_geometry_and_output(session, assembly):
    case = CASES[0]
    packed = [domain(row) for row in case["domains"]]
    obstacles, leases = obstacle_variants(session, assembly)
    outputs = [
        StackSession(session.engine).run(
            [r[0] for r in packed], settings(case["settings"]), obstacles=[bone]
        )[0]
        for bone in obstacles
    ]
    assert_same_output(*outputs)
    assert [(r["status"], r["message"]) for r in outputs[0].values()] == [
        (r["status"], r["message"]) for r in outputs[1].values()
    ]
    assert leases


@pytest.mark.parametrize("change", ["provider", "receiver"])
def test_changed_stacking_inputs_match_fresh_native_sessions(session, change):
    from anthroforge.application.tissue_stack_evaluation import evaluate

    _, first, second = tissue_assembly(session)
    target = first if change == "provider" else second
    for amount in (0.021, 0.024, 0.019):
        session.command("tissue.inflation", target=target, changes=dict(amount=amount))
        session.wait(30)
        item = session.document.object(second)
        assert item.final_result.status == "ready"
        accepted = session.assets[item.final_result.asset].mesh
        session.engine.stack_sessions.clear()
        fresh = evaluate(session.engine, session.document, session.resources.snapshot(), item, 0)
        np.testing.assert_array_equal(accepted.array(0), fresh.mesh.array(0))
        np.testing.assert_array_equal(accepted.array(3), fresh.mesh.array(3))
