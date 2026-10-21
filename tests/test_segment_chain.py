import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.segment_chain import Segment, SegmentChain
from anthroforge.native.mesh import GeometryEngine
from anthroforge.native.segment_chain import construct

REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_segments.json").read_text()
)


def source_settings(case):
    p = case["parameters"]
    lengths = [p[key + " Length"] for key in ("Metacarpal", "Proximal", "Middle", "Distal")]
    radii = [p[key + " Thickness"] for key in ("Metacarpal", "Base", "Middle", "Tip")]
    bends = [0, *[p[key + " Bend"] for key in ("Proximal", "Middle", "Distal")]]
    segments = tuple(
        Segment(length, radius, bend, sides=11 if i == 1 else 12)
        for i, (length, radius, bend) in enumerate(zip(lengths, radii, bends, strict=True))
    )
    return SegmentChain(
        segments,
        p["Spread Angle"],
        profile=tuple(x for row in case["profile"] for x in row),
        unite=False,
    )


@pytest.mark.parametrize("case", REFERENCE["cases"], ids=lambda c: c["name"])
def test_native_segment_chain_matches_node_geometry(case):
    engine = GeometryEngine()
    mesh = construct(engine, source_settings(case), 0)
    np.testing.assert_allclose(mesh.array(0), case["mesh"]["vertices"], atol=3e-6)


def test_parameter_edits_persist_and_undo(session, tmp_path):
    entity = session.command("primitive.create", kind="SEGMENT_CHAIN")
    session.wait()
    assert not session.scheduler.errors
    session.command("chain.segment", entity=entity, index=1, length=0.7, bend=0.6)
    session.wait()
    assert session.document.entity(entity).primitive.chain.segments[1].length == 0.7
    path = tmp_path / "chain.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("chain.configure", entity=entity, spread=0.4)
    session.command("undo")
    assert session.document.entity(entity).primitive.chain.spread == 0
    session.command("open", path=str(path))
    assert session.document.entity(entity).primitive.chain.segments[1].bend == 0.6


def test_unstable_membership_rejected_but_whole_target_deformation_allowed(session):
    entity = session.command("primitive.create", kind="SEGMENT_CHAIN")
    session.wait()
    control = session.command("control.create", entity=entity)
    with pytest.raises(ValueError, match="changing geometry membership"):
        session.command("deformer.add", control=control, target={"owner": entity}, indices=[0])
    session.command("deformer.add", control=control, target={"owner": entity})
    session.command("chain.segment", entity=entity, index=0, bend=0.2)
    session.wait(timeout=5)
    assert not session.scheduler.errors


def test_union_returns_closed_nonempty_geometry():
    engine = GeometryEngine()
    source = source_settings(REFERENCE["cases"][0])
    mesh = construct(engine, replace(source, unite=True), 0)
    assert mesh.counts[0] > 0 and mesh.counts[1] > 0
    faces = mesh.array(3)
    edges = np.sort(np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    assert np.all(np.unique(edges, axis=0, return_counts=True)[1] == 2)


def test_segment_sides_and_caps_have_consistent_outward_winding():
    mesh = construct(GeometryEngine(), SegmentChain((Segment(),), unite=False), 0)
    faces = mesh.array(3)
    edges = np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    assert len(np.unique(edges, axis=0)) == len(edges)
    points = mesh.array(0)[faces]
    volume = np.einsum("ij,ij->i", points[:, 0], np.cross(points[:, 1], points[:, 2])).sum() / 6
    assert volume > 0


def test_union_preserves_every_segment_extent_and_disabled_zero_radius():
    settings = SegmentChain((Segment(), Segment(0, 0), Segment(bend=0.4)))
    output = construct(GeometryEngine(), settings, 0)
    reference = construct(
        output.engine,
        replace(settings, unite=False, segments=(settings.segments[0], settings.segments[2])),
        0,
    )
    np.testing.assert_allclose(
        output.array(0).min(axis=0), reference.array(0).min(axis=0), atol=1e-7
    )
    np.testing.assert_allclose(
        output.array(0).max(axis=0), reference.array(0).max(axis=0), atol=1e-7
    )
