"""Constraint witnesses reuse production goals and disclose current target provenance."""

import numpy as np

from tests.test_tissue_target_regions import bind_region, region_scene


def explain(session, target, stage="intrinsic"):
    session.command(
        "tissue.inspect.point", target=target, stage=stage, triangle=0, weights=[0.2, 0.3, 0.5]
    )
    session.wait()
    value = session.command("tissue.inspect.status", kind="point")
    assert value["state"] == "ready", value
    assert not value["report"].get("goal_error"), value
    return value["report"]


def test_source_goal_matches_fixed_result_with_offset(session):
    target, region, _ = region_scene(session)
    session.command(
        "tissue.constraint.update", target=target, constraint=region, changes=dict(offset=0.03)
    )
    session.wait()
    report = explain(session, target)
    row = report["constraints"][0]
    assert row["goal_basis"] == "accepted rest" and row["residual"] < 1e-10
    np.testing.assert_allclose(row["goal"], row["actual"], atol=1e-10)


def test_current_bound_goal_is_distinct_from_manual_accepted_geometry(session):
    target, region, parent = region_scene(session)
    bind_region(session, target, region, parent)
    row = explain(session, target)["constraints"][0]
    assert row["residual"] < 1e-10
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("scp.transform", entity=parent, values=[2.2, 0, 0, 0, 0, 0, 1, 1, 1])
    session.wait()
    changed = explain(session, target)["constraints"][0]
    assert changed["goal_basis"] == "current retained target binding"
    np.testing.assert_allclose(changed["goal"], np.array(row["goal"]) + [0.2, 0, 0], atol=1e-10)
    assert abs(changed["residual"] - 0.2) < 1e-10
