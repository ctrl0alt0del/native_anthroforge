"""Routing and advisory collision queries consume explicit anatomy surface providers."""

import numpy as np

from anthroforge.core.results import Port
from anthroforge.core.routing_obstacles import references, targets
from tests.test_anchor_operations import CUBE
from tests.test_automatic_routing import ready
from tests.test_fiber_collision_issues import collisions
from tests.test_fiber_creation import bind, path
from tests.test_tissue_workflow import assembly


def radial(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    point = session.command("construction.point.create", position=[0, 0, 2])
    anchor = session.command("anchor.create", source=point, parent=bone)["object_id"]
    session.wait()
    tissue = session.command("tissue.create", source=anchor, preset="CUSTOM")
    session.command("tissue.inflation", target=tissue, changes=dict(amount=0.3))
    session.wait()
    assert session.document.object(tissue).final_result.status == "ready"
    return bone, tissue


def line(session, engine="ROUTED"):
    key = session.command(
        "curve.create", engine=engine, points=[dict(position=[x, 0, 2]) for x in (-1, 1)]
    )
    return ready(session, key)


def test_automatic_tissue_obstacle_routes_and_exclusion_restores_straight_path(session):
    _, tissue = radial(session)
    item = line(session)
    assert tissue in targets(session.document, item)
    assert any(
        r.target == tissue and r.role == "TISSUE_FINAL" for r in references(session.document, item)
    )
    assert np.max(np.linalg.norm(path(session, item.id)[:, 1:3] - [0, 2], axis=1)) > 0.2
    session.command("curve.engine_settings", curve=item.id, excluded_obstacles=[tissue])
    ready(session, item.id)
    np.testing.assert_allclose(
        path(session, item.id)[:, 1:3], np.tile([0, 2], (len(path(session, item.id)), 1)), atol=1e-8
    )


def test_manual_tissue_obstacles_follow_final_surface_revisions(session):
    _, tissue = radial(session)
    item = line(session)
    session.command("curve.engine_settings", curve=item.id, obstacles=[tissue])
    item = ready(session, item.id)
    assert targets(session.document, item) == (tissue,)
    assert (
        Port(tissue, "final")
        in session.document.index.structure.dependencies[Port(item.id, "path")]
    )
    session.command("tissue.inflation", target=tissue, changes=dict(amount=0.4))
    changed = ready(session, item.id)
    assert changed.result.revision > item.result.revision
    assert np.max(np.linalg.norm(path(session, item.id)[:, 1:3] - [0, 2], axis=1)) > 0.3


def test_authored_fiber_reports_tissue_contact_without_rerouting(session):
    bone, tissue = radial(session)
    source = line(session, "POLYLINE")
    fiber = bind(session, bone, source.id)
    before = path(session, fiber.id)
    session.command("issues.recheck", provider="fiber_collisions.v1")
    session.wait()
    rows = [r for r in collisions(session) if tissue in r["related"]]
    assert rows and rows[0]["evidence"]["surface_role"] == "TISSUE_FINAL"
    np.testing.assert_array_equal(path(session, fiber.id), before)
    assert session.document.object(fiber.id).engine == "POLYLINE"


def test_routed_tissue_source_excludes_own_consumer_but_keeps_explicit_cycle(session):
    bone, _ = radial(session)
    source = line(session)
    fiber = bind(session, bone, source.id)
    tissue = session.command("tissue.create", source=fiber.id, preset="CUSTOM")
    item = ready(session, fiber.id)
    graph = session.document.index.structure.dependencies
    assert tissue in graph.routing_excluded[fiber.id] and not graph.blocked
    assert tissue not in targets(session.document, item)
    session.command("curve.engine_settings", curve=fiber.id, obstacles=[tissue])
    session.wait()
    assert Port(fiber.id, "path") in session.document.index.structure.dependencies.blocked
    assert session.document.object(fiber.id).result.asset == item.result.asset


def test_empty_crop_is_not_an_obstacle_and_restoring_it_recomputes(session):
    _, _, tissue = assembly(session)
    item = line(session)
    session.command(
        "tissue.crop",
        target=tissue,
        changes=dict(enabled=True, origin=[10, 0, 0], normal=[1, 0, 0]),
    )
    changed = ready(session, item.id)
    assert changed.result.revision > item.result.revision
    assert tissue in targets(session.document, changed)
    key = session.document.object(tissue).final_result.asset
    assert session.assets[key].mesh.counts[3] == 0
    session.command("tissue.crop", target=tissue, changes=dict(enabled=False))
    assert ready(session, item.id).result.revision > changed.result.revision


def fail_final(monkeypatch, target):
    from anthroforge.application import tissue_evaluation

    original = tissue_evaluation.EVALUATORS["final"]

    def evaluate(engine, document, resources, item, cancel):
        if item.id == target:
            raise ValueError("Injected final surface failure")
        return original(engine, document, resources, item, cancel)

    monkeypatch.setitem(tissue_evaluation.EVALUATORS, "final", evaluate)


def test_failed_surface_keeps_unrelated_collision_evidence(session, monkeypatch):
    from tests.test_fiber_collision_issues import scene

    bone, fiber = scene(session)
    tissue = session.command("tissue.create", source=fiber.id, preset="CUSTOM")
    session.wait()
    fail_final(monkeypatch, tissue)
    session.command("evaluate", entities=[tissue])
    session.wait()
    assert session.document.object(tissue).final_result.status == "failed"
    assert any(bone in row["related"] for row in collisions(session))
    rows = session.command("issues.list", filters=dict(code="COLLISION_SURFACE_UNAVAILABLE"))[
        "records"
    ]
    assert any(row["target"] == tissue for row in rows)
