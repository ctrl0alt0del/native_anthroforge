"""Invalid addon-compatible relaxation must not publish as a usable warned result."""

import numpy as np

from anthroforge.native import mesh_quality
from tests.conftest import CUBE
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import surface


def curved_membrane(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    fibers = []
    for y in (-0.2, 0.2):
        points = [dict(position=p) for p in ((-0.4, y, 0.6), (0, y, 0.7), (0.4, y, 0.6))]
        curve = session.command("curve.create", points=points)
        session.wait()
        fibers.append(bind(session, bone, curve).id)
    return surface(session, fibers, strips=6)


def pouch(session):
    key = session.command("tissue.create", source=curved_membrane(session), preset="POUCH")
    session.command("tissue.configure", target=key, changes=dict(reverse=True))
    session.command("tissue.relaxation", target=key, changes=dict(mode="NONE"))
    session.wait()
    assert session.document.object(key).result.status == "ready"
    return key


def test_invalid_pouch_retains_accepted_shape_and_explicit_edits_recover(session):
    key = pouch(session)
    accepted = session.document.object(key).result.asset
    session.command("tissue.relaxation", target=key, changes=dict(mode="STATIC_PBD"))
    session.wait()
    item = session.document.object(key)
    assert item.intrinsic_result.status == "failed" and item.result.asset == accepted
    assert "self-intersections" in item.intrinsic_result.error
    session.command("tissue.inflation", target=key, changes=dict(amount=0.08))
    session.command("tissue.relaxation", target=key, changes=dict(sagginess=0.2))
    session.wait()
    verify_recovery(session, key, accepted)


def verify_recovery(session, key, accepted):
    item = session.document.object(key)
    assert item.result.status == "ready" and item.result.asset != accepted
    rest = session.assets[item.rest_result.asset].mesh
    output = session.assets[item.intrinsic_result.asset].mesh
    assert mesh_quality.deformation(rest, output).new_crossings == 0
    count = rest.counts[0] // 2
    np.testing.assert_array_equal(rest.array(0)[count:], output.array(0)[count:])
    assert item.diagnostics[0].status in ("CONVERGED", "ITERATION_LIMIT")
