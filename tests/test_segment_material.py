from dataclasses import replace

import numpy as np

from anthroforge.core.entities import IDENTITY
from anthroforge.native import material_bindings, triangle_material
from anthroforge.native.topology import finalize
from tests.test_material_bindings import records
from tests.test_segment_chain import REFERENCE, construct, source_settings


def changed_chain(source):
    segments = list(source.segments)
    segments[0] = replace(segments[0], length=segments[0].length + 0.2)
    return replace(source, segments=tuple(segments))


def matching_triangle(mesh, minimum=300):
    origins, coords = triangle_material.arrays(mesh)
    triangle = next(i for i, origin in enumerate(origins[1:]) if origin > minimum)
    return triangle, int(origins[triangle + 1]), coords.reshape((-1, 3, 3))[triangle].mean(axis=0)


def test_union_material_location_survives_changed_triangulation(session):
    source = source_settings(next(c for c in REFERENCE["cases"] if c["name"] == "Index"))
    before = construct(session.engine, replace(source, unite=True), 0)
    after = construct(session.engine, replace(changed_chain(source), unite=True), 0)
    raw = construct(session.engine, changed_chain(source), 0)
    triangle, origin, bary = matching_triangle(before)
    frames = material_bindings.frames(before, after, IDENTITY, records(before, triangle))
    expected = bary @ raw.array(0)[raw.array(3)[origin]]
    np.testing.assert_allclose(frames[0].reshape(4, 4)[:3, 3], expected, atol=1e-7)


def chain_and_child(session):
    parent = session.command("primitive.create", kind="SEGMENT_CHAIN")
    session.wait()
    child = session.command("scp.empty", parent=parent, name="Attachment probe")
    session.command("scp.transform", entity=child, values=[0.05, 0.15, 0, 0, 0, 0, 1, 1, 1])
    session.command(
        "scp.attachment", entity=child, parent_mode="SURFACE_NEAREST", child_mode="OBJECT_ORIGIN"
    )
    session.wait()
    return parent, child


def test_scp_attachment_retains_union_reference_and_roundtrips(session, tmp_path):
    parent, child = chain_and_child(session)
    reference = session.document.entity(child).attachment.material_asset
    session.command("chain.segment", entity=parent, index=1, bend=0.6)
    session.wait()
    assert not session.scheduler.errors
    assert reference in session.assets
    assert session.document.entity(child).status == "ready"
    path = tmp_path / "retained.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.command("open", path=str(path))
    assert session.document.entity(child).attachment.material_asset == reference
    assert triangle_material.arrays(session.assets[reference].mesh)[0].size > 1


def test_material_metadata_survives_deformation_and_finalization(session):
    from anthroforge.native import construction

    source = replace(source_settings(REFERENCE["cases"][1]), unite=True)
    mesh = construct(session.engine, source, 0)
    before = triangle_material.arrays(mesh)
    changed = finalize(construction.deformed(mesh, mesh.array(0) + [0.1, 0.2, 0.3]), None, 0)
    for a, b in zip(before, triangle_material.arrays(changed), strict=True):
        np.testing.assert_array_equal(a, b)
