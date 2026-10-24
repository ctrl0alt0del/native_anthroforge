"""Required shared construction and seam constraints remain coherent across incident curves."""

import numpy as np

from anthroforge.core.mirroring import MirrorInstance
from tests.test_symmetric_construction import curve


def join(session, source, target):
    a, b = session.document.object(source), session.document.object(target)
    session.command(
        "junction.create",
        source=dict(curve=source, point=a.points[0].id),
        targets=[dict(curve=target, point=b.points[0].id)],
    )
    session.wait()


def test_required_junction_peer_is_one_shared_mirrored_construction(session):
    root = session.command("scp.empty", name="Root")
    a = curve(session, [(1, 0, 0), (1, 1, 0)], "POLYLINE")
    b = curve(session, [(1, 0, 0), (2, 0, 0)], "POLYLINE")
    join(session, a, b)
    session.command("primitive.from_curves", curves=[a], kind="BODY", parent=root)
    session.wait()
    session.command("mirror.configure", target=root, enabled=True)
    values = [session.command("mirror.inspect", target=MirrorInstance(k, root).id) for k in (a, b)]
    assert values[0]["junctions"][0]["id"] == values[1]["junctions"][0]["id"]
    assert all(r["available"] for r in values[0]["junctions"][0]["members"])
    assert len(session.command("mirror.list", source=b)) == 1


def test_editing_other_junction_member_respects_symmetric_seam_and_one_undo(session):
    loop = curve(session, [(0, 0, 0), (1, 1, 0), (0, 2, 0)], "POLYLINE")
    session.command("mirror.loop.create", curve=loop)
    session.wait()
    other = curve(session, [(0, 0, 0), (-1, 0, 0)], "POLYLINE")
    join(session, other, loop)
    before = [session.document.object(key).points for key in (other, loop)]
    session.command(
        "curve.point.update", curve=other, point=before[0][0].id, position=[2, 0.3, 0.1]
    )
    session.wait()
    for key in (other, loop):
        assert_seam(session.document.object(key))
    session.command("undo")
    assert [session.document.object(key).points for key in (other, loop)] == before


def assert_seam(item):
    assert item.result.status == "ready", item.result.error
    np.testing.assert_allclose(item.points[0].position, [0, 0.3, 0.1])
