import pytest


def test_type_assignment_is_explicit_and_mirrors_do_not_create_instances(session, assembly):
    root, child = assembly
    key = session.command("catalogue.type.create", name="Humerus", aliases=["Arm bone"])
    session.command("catalogue.assign", target=child, type_id=key, side="LEFT")
    result = session.command("catalogue.inspect")
    assert result["assignments"] == [dict(target=child, type_id=key, side="LEFT", label="")]
    assert root not in {r["target"] for r in result["assignments"]}
    with pytest.raises(ValueError, match="assignments"):
        session.command("catalogue.type.remove", type_id=key)
    session.command("undo")
    assert not session.command("catalogue.inspect")["assignments"]


def test_review_keeps_decision_but_marks_changed_geometry_outdated(session, assembly):
    _, child = assembly
    key = session.command(
        "review.set", subject=child, dimension="ANATOMY", decision="APPROVED", reviewer="Reviewer"
    )
    assert session.command("review.inspect")["reviews"][0]["freshness"] == "CURRENT"
    session.command("scp.transform", entity=child, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    row = session.command("review.inspect")["reviews"][0]
    assert (row["id"], row["decision"], row["freshness"]) == (key, "APPROVED", "OUTDATED")


def test_queue_claims_types_and_requires_explicit_takeover(session, assembly):
    root, child = assembly
    kind = session.command("catalogue.type.create", name="Shared type")
    first = session.command("reconstruction.queue.add", subject=root, type_id=kind)
    second = session.command("reconstruction.queue.add", subject=child, type_id=kind)
    session.command("reconstruction.queue.claim", work=first, owner="A")
    assert session.command("reconstruction.queue.claim", owner="B") == {"work": None}
    with pytest.raises(ValueError, match="claimed"):
        session.command("reconstruction.queue.claim", work=second, owner="B")
    session.command("reconstruction.queue.claim", work=second, owner="B", takeover=True)
    assert {r["owner"] for r in session.command("reconstruction.queue.inspect")["work"]} == {"B"}


def test_region_survives_pose_change_without_nearest_remapping(session, assembly):
    _, child = assembly
    key = session.command("catalogue.region.set", target=child, name="Patch", triangles=[0, 1])
    original = session.command("catalogue.region.inspect", region=key)
    session.command("scp.transform", entity=child, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    current = session.command("catalogue.region.inspect", region=key)
    assert current["available"] and current["triangles"] == original["triangles"]
    assert current["asset"] == original["asset"]
