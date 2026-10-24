"""Frozen measurements retain the displayed spatial instance and explicit surface stage."""

import numpy as np

from anthroforge.core.mirroring import MirrorInstance
from tests.test_mirror_inspection import mirrored_layers


def point(session, entity, **options):
    return session.command(
        "measurement.point", entity=entity, triangle=0, weights=[0.2, 0.3, 0.5], **options
    )


def test_mirrored_scp_points_are_reflected_and_plane_changes_only_mark_annotations_stale(
    session, assembly
):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True, shift=2)
    original, mirror = reflected_points(session, root, child)
    session.command("measurement.add", start=original, end=mirror)
    before = session.command("measurement.list")[0]
    assert not before["stale"]
    session.command("mirror.configure", target=root, shift=3)
    session.wait()
    after = session.command("measurement.list")[0]
    assert after["stale"] and after["distance"] == before["distance"]
    assert after["end"]["position"] == before["end"]["position"]


def reflected_points(session, root, child):
    original, mirror = point(session, child), point(session, MirrorInstance(child, root).id)
    expected = session.engine.world_point(
        session.document.mirrors.rules[root].frame, original["position"]
    )
    np.testing.assert_allclose(mirror["position"], expected)
    return original, mirror


def test_mirrored_tissue_stage_and_construction_measurements_roundtrip(session, tmp_path):
    bone, first, second, mirror = mirrored_layers(session)
    a = point(session, mirror, stage="rest")
    membrane = session.document.object(second).source
    b = point(session, MirrorInstance(membrane, bone).id)
    session.command("measurement.add", start=a, end=b)
    assert not session.command("measurement.list")[0]["stale"]
    filename = str(tmp_path / "measurements.anthroforge")
    session.command("save", path=filename, blocked_policy="wait")
    session.command("open", path=filename)
    row = session.command("measurement.list")[0]
    assert row["start"]["stage"] == "rest" and not row["stale"]
